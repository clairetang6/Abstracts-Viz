# -*- coding: utf-8 -*-
"""
Created on Fri Dec 11 13:44:34 2015

@author: Claire Tang
"""

import nltk
import string
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.cluster import hierarchy

lemmatizer = nltk.stem.wordnet.WordNetLemmatizer()

def preprocess_abstract(abstract):
    if abstract is None:
        return ""
    #separate words with dashes - and then remove punctuation. 
    abstract = abstract.lower().translate(str.maketrans("-", " "))
    text = remove_punctuation(abstract)
    #lemmatize and rejoin to create processed abstract
    tokens = nltk.word_tokenize(text)
    lemmas = [lemmatizer.lemmatize(word) for word in tokens if not word[0] in set(string.digits)]
    return " ".join(lemmas)

def remove_punctuation(s):
    return "".join(c for c in s if c not in set(string.punctuation))

def preprocess_abstracts(abstracts):
    return [preprocess_abstract(ab) for ab in abstracts]

def get_abstract_distance_matrix(abstracts, tfidf=None):
    if tfidf is None:
        tfidf = TfidfVectorizer(stop_words="english")
    tfs = tfidf.fit_transform(abstracts).toarray()
    distance_matrix = np.zeros((tfs.shape[0], tfs.shape[0]))
    for i in range(tfs.shape[0]):
        for j in range(tfs.shape[0]):
            distance_matrix[i][j] = 1 - np.dot(tfs[i], tfs[j])
    return distance_matrix

def get_hierarchy_linkage_from_tfs(tfs):
    Z = hierarchy.linkage(tfs, method="ward")
    return Z