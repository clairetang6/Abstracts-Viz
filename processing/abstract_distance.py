# -*- coding: utf-8 -*-
"""
Created on Sun Jul 26 23:19:33 2015

@author: Claire Tang
"""

import pubmed_interface
import nltk
import json
import string
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

stemmer = nltk.stem.porter.PorterStemmer()

def save_abstracts_and_titles(author):
    dois = pubmed_interface.search_pubmed_author(author, retmax=20)
    titles = []
    abstracts = []
    for doi in dois:
        article = pubmed_interface.PubMedObject(doi)
        article.download()
        article.fill_data()
        titles.append(article.title)
        abstracts.append(article.title)
        
    with open('%s.txt'%author.replace(' ', '') , 'w') as f:
        json.dump({'titles': titles, 'abstracts': abstracts}, f)
    
    return titles, abstracts


def tokenize(text):
    tokens = nltk.word_tokenize(text)
    stems = [stemmer.stem(word) for word in tokens if not word[0] in ['0','1','2','3','4','5','6','7','8','9']]
    return stems


def compute_distance_matrix(abstracts):
    abstracts = [ab.lower().translate(str.maketrans("-", " ")) for ab in abstracts]
    abstracts = [''.join(c for c in ab if c not in set(string.punctuation)) for ab in abstracts]
    
    tfidf = TfidfVectorizer(tokenizer=tokenize, stop_words="english")
    tfs = tfidf.fit_transform(abstracts).toarray()
    
    distance_matrix = np.zeros((tfs.shape[0], tfs.shape[0]))
    for i in range(tfs.shape[0]):
        for j in range(tfs.shape[0]):
            distance_matrix[i][j] = 1 - np.dot(tfs[i], tfs[j])
    
    return distance_matrix
    
        
        
        

