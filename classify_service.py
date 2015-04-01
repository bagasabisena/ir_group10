from web import db, models
from textblob import TextBlob, WordList
from textblob.classifiers import NaiveBayesClassifier, basic_extractor, _get_words_from_dataset, _get_document_tokens
from textblob.utils import lowerstrip
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
import csv
import codecs


def stopword_stem_bigram_extractor(document, train_set):
    # strip punctuation and lower case all words
    lowstrip_s = TextBlob(lowerstrip(document, all=False))

    # remove stop words
    non_stopwords_s = [word for word in lowstrip_s.words
                       if word not in stopwords.words('english')]
    # stem the words
    snowball_stemmer = SnowballStemmer('english')
    stem_s = [snowball_stemmer.stem(word) for word in non_stopwords_s]

    # create bigrams
    bigrams = stem_s + zip(stem_s[0:], stem_s[1:])

    # return the feature
    return dict([(ngram, True) for ngram in bigrams])


def test_extractor(document, train_set):
    """A basic document feature extractor that returns a dict indicating
    what words in ``train_set`` are contained in ``document``.

    :param document: The text to extract features from. Can be a string or an iterable.
    :param list train_set: Training data set, a list of tuples of the form
        ``(words, label)``.
    """
    word_features = _get_words_from_dataset(train_set)
    tokens = _get_document_tokens(document)
    features = dict(((u'contains({0})'.format(word), (word in tokens))
                                            for word in word_features))

    print tokens
    return features


def stopword_stem_extractor(document):
    # strip punctuation and lower case all words
    lowstrip_s = TextBlob(lowerstrip(document, all=False))

    # remove stop words
    non_stopwords_s = [word for word in lowstrip_s.words
                       if word not in stopwords.words('english')]
    # stem the words
    snowball_stemmer = SnowballStemmer('english')
    stem_s = [snowball_stemmer.stem(word) for word in non_stopwords_s]

    return dict([(word, True) for word in stem_s])


def stopword_extractor(document):
    # strip punctuation and lower case all words
    lowstrip_s = TextBlob(lowerstrip(document, all=False))

    # remove stop words
    non_stopwords_s = [word for word in lowstrip_s.words
                       if word not in stopwords.words('english')]

    return dict([(word, True) for word in non_stopwords_s])


def dummy_extractor(document, train_set):
    print 'document: ' + document
    print train_set
    return False


tips = models.Tip.query.all()

labeled = []
unlabeled = []
all_data_labeled = []
all_data_unlabeled = []

f = open('service2.csv', 'rb')
try:
    reader = csv.reader(f, dialect="excel")
    # skip header
    next(reader, None)

    for r in reader:
        s = r[0].decode('utf-8')

        if not r[2]:
            unlabeled.append(s)
            all_data_unlabeled.append((s, r[1]))
        else:
            labeled.append((s, r[2]))
            all_data_labeled.append((s, r[1], r[2]))

finally:
    f.close()


train_data = labeled[:750]
test_data = labeled[750:]

# turns out basic feature extractor from TextBlob works best
# need to explore why
print "training naive bayes classifier for service"
print "%d training and %d test" % (len(train_data), len(test_data))
cl = NaiveBayesClassifier(train_data, feature_extractor=basic_extractor)
print "accuracy: %f" % cl.accuracy(test_data)

# classify unlabeled data and extract sentiment
print "classify unlabeled data and extract sentiment"
f = open('service3.csv', 'wt')
try:
    writer = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)
    # write header
    writer.writerow(('sentence', 'tip_id', 'label', 'ph'))

    # write labeled data
    for data in all_data_labeled:
        # encoding problem, ignore for now
        s = data[0].encode('ascii', 'ignore')
        writer.writerow((s, data[1], data[2],
                        TextBlob(s).sentiment.polarity))

    # write unlabeled data
    for data in all_data_unlabeled:
        s = data[0].encode('ascii', 'ignore')
        label = cl.classify(s)
        writer.writerow((s, data[1],
                        label, TextBlob(s).sentiment.polarity))
finally:
    f.close()
