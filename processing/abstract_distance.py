# -*- coding: utf-8 -*-
"""
Created on Sun Jul 26 23:19:33 2015

@author: Claire Tang
"""

import asyncio
from . import pubmed_interface
import nltk
import json
import string
import itertools
from collections import Counter
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.cluster import hierarchy
import datetime

from database import create_db
from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind=create_db.engine)
from database import models
session = Session()

stemmer = nltk.stem.porter.PorterStemmer()

loop = asyncio.get_event_loop()

@asyncio.coroutine
def save_abstracts_and_titles(author, retmax=100):
    pmids = yield from pubmed_interface.search_pubmed(author, search_author=True, retmax=retmax)
    pm_articles, db_articles = get_article_lists(pmids)
    yield from pubmed_interface.download_articles(pm_articles)
    
    for article in pm_articles:
        article.fill_data()

    titles = []
    abstracts_processed = []
    years_months = []  
    authors_all_articles = []
    
    for article in pm_articles:
        titles.append(article.title)
        years_months.append((article.pub_year, article.pub_month))
        abstract_processed = process_abstract(article.abstract)
        authors_all_articles.append(article.authors)        
        authors = json.dumps(article.authors)
        save_article(article, abstract_processed.encode('utf-8'), authors.encode('utf-8'))
        abstracts_processed.append(abstract_processed)
    
    for article in db_articles:
        titles.append(article.title)
        years_months.append((article.pub_year, article.pub_month))
        abstracts_processed.append(article.abstract_processed.decode('utf-8'))
        authors_all_articles.append(json.loads(article.authors.decode('utf-8')))
   
    dataset = get_dataset(titles, abstracts_processed, years_months, pmids, authors_all_articles)
    save_dataset(author, dataset)

def get_article_lists(pmids):
    pm_articles = []
    db_articles = []
    for pmid in pmids:    
        article = session.query(models.Article).filter_by(pmid=pmid).first()
        if article is None:
            pm_articles.append(pubmed_interface.PubMedObject(pmid))
        else:
            db_articles.append(article)
    return pm_articles, db_articles
    
def save_article(article, abstract_processed, authors):
    session.add(models.Article(pmid=article.pmid, title=article.title, pub_year=article.pub_year, pub_month=article.pub_month, abstract_processed=abstract_processed, authors=authors))
    session.commit()   
    
def save_dataset(name, dataset):
    date = datetime.date.today()
    session.add(models.Scientist(name=name, dataset=json.dumps(dataset).encode('utf-8'), date_created=date))
    session.commit() 

def process_abstract(abstract):
    #separate words with dashes - and then remove punctuation. 
    abstract = abstract.lower().translate(str.maketrans("-", " "))
    return ''.join(c for c in abstract if c not in set(string.punctuation))
     
def tokenize(text):
    tokens = nltk.word_tokenize(text)
    stems = [stemmer.stem(word) for word in tokens if not word[0] in ['0','1','2','3','4','5','6','7','8','9']]
    return stems


def get_dataset(titles, abstracts, years_months, pmids, authors):
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
    dists[dists<0] = 0
    
    Z = hierarchy.linkage(dists, method='single')
    Z2 = hierarchy.dendrogram(Z)
    ordering = np.array(Z2['leaves'])
    
    ordered_distance_matrix = np.copy(distance_matrix)
    ordered_distance_matrix = ordered_distance_matrix[:, ordering]
    ordered_distance_matrix = ordered_distance_matrix[ordering, :]
    
    years, months = zip(*years_months)
    years = np.array([int(y) if y != '' else np.NaN for y in years]).astype('float')
    months = np.array([int(m) if m != '' else np.NaN for m in months]).astype('float')
    months[np.isnan(years)] = np.NaN
    
    max_year = np.nanmax(years)
    min_year = np.nanmin(years)
    
    pub_time = years + (months - 1)/12
    min_pub_time = min_year
    range_pub_time = max_year + 1 - min_year
    norm_years = (pub_time - min_pub_time)/range_pub_time
    years[np.isnan(years)] = -1
    norm_years[np.isnan(norm_years)] = -1
    years = years.tolist()
    norm_years = norm_years.tolist()
    
    authors = list(itertools.chain(*authors))
    authors_count = Counter(authors)
    authors_most_common = authors_count.most_common(10)
    
    dataset = {'nodes': [{
            'name' : titles[ordering[i]], 
            'year': years[ordering[i]],
            'normYear': norm_years[ordering[i]],
            'pmid': pmids[ordering[i]]
        } for i in range(tfs.shape[0])], 
        'authors': authors_most_common,
        'distance_matrix': np.around(ordered_distance_matrix, decimals=3).tolist(),
        'minYear': {'year': min_year, 'normYear': (min_year - min_pub_time)/range_pub_time},
        'maxYear': {'year': max_year + 1, 'normYear': (max_year + 1 - min_pub_time)/range_pub_time}}
    
    return dataset
    
        
        
        

