# -*- coding: utf-8 -*-
"""
Created on Sun Jul 26 23:19:33 2015

@author: Claire Tang
"""

from . import pubmed_interface
import nltk
import json
import string
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.cluster import hierarchy

stemmer = nltk.stem.porter.PorterStemmer()

def save_abstracts_and_titles(author):
    dois = pubmed_interface.search_pubmed_author(author, retmax=100)
    titles = []
    abstracts = []
    for doi in dois:
        article = pubmed_interface.PubMedObject(doi)
        article.download()
        article.fill_data()
        titles.append(article.title)
        abstracts.append(article.abstract)
        
    with open('%s.txt'%author.replace(' ', '') , 'w') as f:
        json.dump({'titles': titles, 'abstracts': abstracts}, f)
    
    return titles, abstracts


def tokenize(text):
    tokens = nltk.word_tokenize(text)
    stems = [stemmer.stem(word) for word in tokens if not word[0] in ['0','1','2','3','4','5','6','7','8','9']]
    return stems


def get_dataset(titles, abstracts):
    #separate words with dashes - and then remove punctuation. 
    abstracts = [ab.lower().translate(str.maketrans("-", " ")) for ab in abstracts]
    abstracts = [''.join(c for c in ab if c not in set(string.punctuation)) for ab in abstracts]
    
    tfidf = TfidfVectorizer(tokenizer=tokenize, stop_words="english")
    tfs = tfidf.fit_transform(abstracts).toarray()
    
    distance_matrix = np.zeros((tfs.shape[0], tfs.shape[0]))
    for i in range(tfs.shape[0]):
        for j in range(tfs.shape[0]):
            distance_matrix[i][j] = 1 - np.dot(tfs[i], tfs[j])
    
    dists = []
    for i in range(0, tfs.shape[0]-1):
        for j in range(i+1, tfs.shape[0]):
            dists.append( 1 - np.dot(tfs[i],tfs[j]))
    dists = np.array(dists)
    
    Z = hierarchy.linkage(dists, method='single')
    Z2 = hierarchy.dendrogram(Z)
    ordering = np.array(Z2['leaves'])
    
    ordered_distance_matrix = np.copy(distance_matrix)
    ordered_distance_matrix = ordered_distance_matrix[:, ordering]
    ordered_distance_matrix = ordered_distance_matrix[ordering, :]
    
    dataset = {'nodes': [{'name' : titles[ordering[i]]} for i in range(tfs.shape[0])], 'distance_matrix': np.around(ordered_distance_matrix, decimals=3).tolist()}
    
    return dataset
    
        
        
        

