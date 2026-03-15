import re
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords, wordnet

stop_words = set(stopwords.words("english"))


def preprocess(text):

    text = text.lower()
    text = re.sub(r"[^a-zA-Z\s]", " ", text)
    # tokenize
    words = word_tokenize(text)

    # remove stopwords and short words
    clean_words = []
    for word in words:
        if word not in stop_words and len(word) > 2:
            clean_words.append(word)

    return clean_words


def expand_words(words):

    expanded = set(words)

    for word in words:
        for syn in wordnet.synsets(word)[:2]:   # limit synsets to avoid too many expansions
            for lemma in syn.lemmas()[:2]:

                synonym = lemma.name().lower().replace("_", " ")
                expanded.add(synonym)

    return list(expanded)