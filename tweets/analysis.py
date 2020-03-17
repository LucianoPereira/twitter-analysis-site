import tweepy
import json
import datetime
import pandas as pd
from pandas.io.json import json_normalize

# WORDCLOUD
import numpy as np
from PIL import Image
from matplotlib import pyplot as plt
from wordcloud import WordCloud, STOPWORDS
import codecs

# Cleanup
import re
import string

# CountVectorizer + lematización
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer

# Generating and training LDA model
from sklearn.decomposition import LatentDirichletAllocation

import os

# Api Authentication Details
consumer_key = '5E2oMO7ZHGElss9cdaLY34x7b'
consumer_secret = 'fwjNRItWWRZ4ftRfwxBSHCwpGY5rth7cKKiZqY06Rru0KECfxi'
access_token = '1031238436064243718-YKGcYZF1yAKAcJTttGNXhAWpHWA4oh'
access_token_secret = 'U0u3Lq29f7PpOfO12q3fHX4nPhtlOV9fqXpEqDHlFbOqt'


# Cleanup for WordClouds - We make all words lowercase, delete simbols and links, then separate each word

def cleanup(sentence):
    cleanup_re1 = re.compile('[^a-z]+')
    cleanup_re2 = re.compile('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    if type(sentence) is str:
        sentence = sentence.lower()
        sentence = sentence.replace("’", "")
        sentence = sentence.replace("'", "")
        sentence = cleanup_re2.sub(' ', sentence).strip()
        sentence = cleanup_re1.sub(' ', sentence).strip()
    return sentence


def save_tweets_in_file(filepath, api, username, tweet_count):
    file = open(filepath, 'w')
    counter = 0
    for status in tweepy.Cursor(api.user_timeline, screen_name=username, count=tweet_count, tweet_mode="extended",
                                include_rts=False).items():
        file.write(json.dumps(status._json) + '\n')
        counter += 1
        if counter >= tweet_count:
            return
    file.close()


def save_user_tweets(api, username, tweet_count=300):
    filename = ('tweet' + username + '.json').replace(" ", "")
    print("tweets saved at: " + filename)
    save_tweets_in_file(filename, username, tweet_count)
    return


def tweets_dataframe(username, api, tweet_count):
    dataframe = pd.DataFrame()
    for status in tweepy.Cursor(api.user_timeline, screen_name=username, count=tweet_count, tweet_mode="extended",
                                include_rts=False).items():
        tweet = json.dumps(status._json)
        tweet = json_normalize(json.loads(tweet))
        df_item = pd.DataFrame(tweet)
        dataframe = dataframe.append(df_item, ignore_index=True)
    return dataframe


class LemmaCountVectorizer(CountVectorizer):

    def build_analyzer(self):
        lemm = WordNetLemmatizer()
        analyzer = super(LemmaCountVectorizer, self).build_analyzer()
        return lambda doc: (lemm.lemmatize(w) for w in analyzer(doc))


class TweetAnalysis:
    def __init__(self, dataframe, tweet_list):
        self.dataframe = dataframe
        self.tweet_list = tweet_list
        self.text = self.prepare_wordcloud_data()

    def most_mentioned_dict(self):
        # Returns a dictionary, its keys are the users mentioned and the value the amount of times they meantioned them
        most_mentioned = {}
        for tweet in self.tweet_list:
            if '@' in tweet:
                lista = re.findall("[@]\w+", tweet)
                for elem in lista:
                    if elem not in most_mentioned:
                        most_mentioned[elem] = 1
                    else:
                        most_mentioned[elem] += 1
        print(most_mentioned.values())
        return most_mentioned

    # Creating word list, containing every word from every tweet
    def prepare_wordcloud_data(self):
        wc_word_list = []
        for tweets in self.tweet_list:
            for word in tweets.split():
                wc_word_list.append(word)
        wc_word_string = " ".join(wc_word_list)
        return wc_word_string

    # Generating the wordcloud
    @staticmethod
    def generate_tweet_wordcloud(text):
        module_dir = os.path.dirname(__file__)  # get current directory
        file_path = os.path.join(module_dir, 'wordcloud/twitter11.png')
        img = Image.open(file_path)
        hcmask = np.array(img)
        wc = WordCloud(width=6500, height=4300, background_color='black', mask=hcmask, max_words=300, max_font_size=100,
                       stopwords=STOPWORDS)
        wc.generate(text)
        # plt.figure(figsize=[60,40])
        # plt.title('@' + name_search, fontsize=70)
        # plt.imshow(wc.recolor(colormap='Pastel2',random_state=17), alpha=0.98)
        # plt.axis('off')

        return wc

    # saves the wordcloud in the project (tweets/images/wordcloud.png)
    def save_tweet_wordcloud(self, text, filename):
        wc = self.generate_tweet_wordcloud(text)
        module_dir = os.path.dirname(__file__)  # get current directory
        wc_path = os.path.join(module_dir, filename)
        print(wc_path)
        wc.to_file(wc_path)

    # return 5 most liked tweets
    def get_most_liked_tweets(self, n):
        most_liked_tweets = self.dataframe.nlargest(n, 'favorite_count')
        return ["https://twitter.com/{}/status/{}".format(row['user.screen_name'], row.id) for index, row in
                most_liked_tweets.iterrows()]

    # return 5 most retweeted tweets
    def get_most_retweeted_tweets(self, n):
        most_liked_tweets = self.dataframe.nlargest(n, 'retweet_count')
        return ["https://twitter.com/{}/status/{}".format(row['user.screen_name'], row.id) for index, row in
                most_liked_tweets.iterrows()]

    # Instancio el count vectorizer (Genera Bag of Words en base a los tweets) y le hago el fit
    def bag_of_words_from_tweets(self):
        text_list = [tweet for tweet in self.tweet_list]
        countvec_lda = LemmaCountVectorizer(max_df=0.95, min_df=5, stop_words="english", decode_error='ignore')
        bag_of_words = countvec_lda.fit_transform(text_list)
        # Me guardo la matriz BOW y los nombres de las features, es decir las palabras
        return bag_of_words, countvec_lda.get_feature_names()

    @staticmethod
    def lda_model(x, n):
        lda = LatentDirichletAllocation(n_components=n,
                                        learning_method='online',
                                        learning_offset=50.,
                                        random_state=0,
                                        n_jobs=-1)
        lda_Z = lda.fit_transform(x)
        return lda_Z, lda

    # Printing each topic generated by the LDA model
    @staticmethod
    def get_top_words(model, feature_names, n_top_words):
        topic_words = []
        for index, topic in enumerate(model.components_):
            message = "\nTopic #{}:".format(index)
            message += " ".join([feature_names[i] for i in topic.argsort()[:-n_top_words - 1:-1]])
            print(message)
            print("=" * 70)
            topic_words.append(message)
        return topic_words


def lda_topics_wc(lda_model, tf_feature_names):
    topic_list = [topic for topic in lda_model.components_]
    topic_word_list = []
    for item in topic_list:
        topic_word_list.append(" ".join([tf_feature_names[i] for i in item.argsort()[:-50 - 1:-1]]))
    return topic_word_list


def analysis():
    # Authenticating the Application
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    api = tweepy.API(auth)

    # TWEETS A DATAFRAME
    name_search = 'elonmusk'
    df = tweets_dataframe(name_search, api, 300)
    df_text = df['full_text']
    # Lowercase tweet list, with no simbols
    tweet_list = df_text.apply(cleanup)
    tweet_analysis = TweetAnalysis(df, tweet_list)
    tweet_analysis.save_tweet_wordcloud(tweet_analysis.text, 'images\wordcloud.png')
    analysis_context = {}
    analysis_context['most_liked_tweets'] = tweet_analysis.get_most_liked_tweets(5)
    analysis_context['most_retweeted_tweets'] = tweet_analysis.get_most_retweeted_tweets(5)

    tweet_bow, tf_feature_names = tweet_analysis.bag_of_words_from_tweets()

    # print(tweet_bow.shape)
    # print(tweet_bow.toarray())

    topic_amount = 3

    analysis_context['topic_amount'] = topic_amount

    lda_z, lda_model = tweet_analysis.lda_model(tweet_bow, topic_amount)

    n_top_words = 40
    # imprimo las top Words

    analysis_context['topic_words'] = tweet_analysis.get_top_words(lda_model, tf_feature_names, n_top_words)

    lda_topic_list = lda_topics_wc(lda_model, tf_feature_names)
    for i, item in enumerate(lda_topic_list):
        tweet_analysis.save_tweet_wordcloud(item, 'images/topic{}.png'.format(i))
