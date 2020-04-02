# CountVectorizer + lematización
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer

# Generating and training LDA model
from sklearn.decomposition import LatentDirichletAllocation


class LemmaCountVectorizer(CountVectorizer):

    def build_analyzer(self):
        lemm = WordNetLemmatizer()
        analyzer = super(LemmaCountVectorizer, self).build_analyzer()
        return lambda doc: (lemm.lemmatize(w) for w in analyzer(doc))


def lda_model(x, n):
    lda = LatentDirichletAllocation(n_components=n,
                                    learning_method='online',
                                    learning_offset=50.,
                                    random_state=0,
                                    n_jobs=-1)
    lda_z = lda.fit_transform(x)
    return lda_z, lda


def lda_topics_wc(lda, tf_feature_names):
    topic_list = [topic for topic in lda.components_]
    topic_word_list = []
    for item in topic_list:
        topic_word_list.append(" ".join([tf_feature_names[i] for i in item.argsort()[:-50 - 1:-1]]))
    return topic_word_list

