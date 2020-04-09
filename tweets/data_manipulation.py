import tweepy
import json
import pandas as pd
from pandas.io.json import json_normalize
from .ml_models import LemmaCountVectorizer
from django.http import Http404
# WORDCLOUD
import numpy as np
from PIL import Image
from matplotlib import pyplot as plt
from wordcloud import WordCloud, STOPWORDS

# Cleanup
import re

import os


def user_tweets_to_dataframe(username, api, tweet_count):
    dataframe = pd.DataFrame()
    try:
        cursor = tweepy.Cursor(api.user_timeline, screen_name=username, count=tweet_count, tweet_mode="extended",
                               include_rts=False).items(tweet_count)
        for status in cursor:
            tweet = json.dumps(status._json)
            tweet = json_normalize(json.loads(tweet))
            df_item = pd.DataFrame(tweet)
            dataframe = dataframe.append(df_item, ignore_index=True, sort=False)
    except tweepy.TweepError:
        raise Http404
    return dataframe


def topic_tweets_to_dataframe(topic, api, tweet_count):
    dataframe = pd.DataFrame()
    try:
        cursor = tweepy.Cursor(api.search, q=topic, result_type="mixed", count=tweet_count, tweet_mode="extended",
                               include_rts=False).items(tweet_count)
        for status in cursor:
            tweet = json.dumps(status._json)
            tweet = json_normalize(json.loads(tweet))
            df_item = pd.DataFrame(tweet)
            dataframe = dataframe.append(df_item, ignore_index=True, sort=False)
    except tweepy.TweepError:
        raise Http404
    return dataframe


def df_to_tweet_list(dataframe):
    return dataframe['full_text']


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


# Creating a string, containing every word from every tweet
def prepare_wordcloud_data(tweet_list):
    wc_word_list = []
    for tweets in tweet_list:
        for word in tweets.split():
            wc_word_list.append(word)
    wc_word_string = " ".join(wc_word_list)
    return wc_word_string


# Generating the wordcloud
def generate_tweet_wordcloud(text, mask=None):
    if mask:
        module_dir = os.path.dirname(__file__)  # get current directory
        wc_mask = "wordcloud/" + mask
        file_path = os.path.join(module_dir, wc_mask)
        img = Image.open(file_path)
        hcmask = np.array(img)
        wc = WordCloud(width=1920, height=1080, background_color='black',
                       mask=hcmask, max_words=300, max_font_size=100,
                       stopwords=STOPWORDS)
    else:
        wc = WordCloud(width=6500, height=4300, background_color='black', max_words=300,
                       max_font_size=100,
                       stopwords=STOPWORDS)
    wc.generate(text)
    # plt.figure(figsize=[60,40])
    # plt.title('@' + name_search, fontsize=70)
    # plt.imshow(wc.recolor(colormap='Pastel2',random_state=17), alpha=0.98)
    # plt.axis('off')

    return wc


# saves the wordcloud in the project (tweets/images/wordcloud.png)
def save_tweet_wordcloud(text, filename, mask=None):
    wc = generate_tweet_wordcloud(text, mask)
    module_dir = os.path.dirname(__file__)  # get current directory
    wc_path = os.path.join(module_dir, filename)
    print(wc_path)
    wc.to_file(wc_path)


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


def save_user_tweets(username, tweet_count=300):
    filename = ('tweet' + username + '.json').replace(" ", "")
    print("tweets saved at: " + filename)
    save_tweets_in_file(filename, username, tweet_count)


def get_most_mentioned_dict(tweet_list, n):
    # Returns a dictionary, its keys are the users mentioned and the value the amount of times they meantioned them
    most_mentioned_dict = {}
    for tweet in tweet_list:
        if '@' in tweet:
            lista = re.findall("[@]\w+", tweet)
            for elem in lista:
                if elem not in most_mentioned_dict:
                    most_mentioned_dict[elem] = 1
                else:
                    most_mentioned_dict[elem] += 1
    most_mentioned_order_dict = {k: v for k, v in sorted(most_mentioned_dict.items(),
                                                         key=lambda item: item[1], reverse=True)}
    return most_mentioned_order_dict


# return 5 most liked tweets
def get_most_liked_tweets(df, n):
    most_liked_tweets = df.nlargest(n, 'favorite_count')
    return ["https://twitter.com/{}/status/{}".format(row['user.screen_name'], row.id) for index, row in
            most_liked_tweets.iterrows()]


# return 5 most retweeted tweets
def get_most_retweeted_tweets(df, n):
    most_liked_tweets = df.nlargest(n, 'retweet_count')
    return ["https://twitter.com/{}/status/{}".format(row['user.screen_name'], row.id) for index, row in
            most_liked_tweets.iterrows()]


# Instancio el count vectorizer (Genera Bag of Words en base a los tweets) y le hago el fit
def bag_of_words_from_tweets(tweet_list):
    text_list = [tweet for tweet in tweet_list]
    countvec_lda = LemmaCountVectorizer(max_df=0.95, min_df=5, stop_words="english", decode_error='ignore')
    bag_of_words = countvec_lda.fit_transform(text_list)
    # Me guardo la matriz BOW y los nombres de las features, es decir las palabras
    return bag_of_words, countvec_lda.get_feature_names()
