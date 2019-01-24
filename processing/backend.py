# -*- coding: utf-8 -*-
"""
Created on Fri Dec 11 13:32:29 2015

@author: Claire Tang
"""

import asyncio
import nltk
import json
import itertools
from collections import Counter
import numpy as np
from . import pubmed_interface
from . import abstract_text
from . import database_interface

loop = asyncio.get_event_loop()

def check_if_author(search_term):
	search_term = name_key(search_term)
	tagged_terms = nltk.pos_tag(nltk.word_tokenize(search_term))
	pos_tags = [t[1] for t in tagged_terms]
	if any(np.array(pos_tags) == 'NNP'):
		return True
	else:
		return False

async def search_pubmed_save_articles_compute_distance_dataset(search_term, retmax=100):
	pmids = await pubmed_interface.search_pubmed(search_term, retmax=retmax)
	pm_articles, db_articles = get_article_lists(pmids)
	await pubmed_interface.download_articles(pm_articles)

	for article in pm_articles:
		article.fill_data()

	titles = []
	abstracts_processed = []
	years_months = []  
	authors_all_articles = []
	
	for article in pm_articles:
		titles.append(article.title)
		years_months.append((article.pub_year, article.pub_month))
		abstract_processed = abstract_text.preprocess_abstract(article.abstract)
		authors_all_articles.append(article.authors)        
		authors = json.dumps(article.authors)
		database_interface.save_article(article, abstract_processed.encode('utf-8'), authors.encode('utf-8'))
		abstracts_processed.append(abstract_processed)
		
	for article in db_articles:
		titles.append(article.title)
		years_months.append((article.pub_year, article.pub_month))
		abstracts_processed.append(article.abstract_processed.decode('utf-8'))
		authors_all_articles.append(json.loads(article.authors.decode('utf-8')))
	
	dataset = await loop.run_in_executor(None, compute_dataset, titles, abstracts_processed, years_months, pmids, authors_all_articles)
	database_interface.save_dataset(search_term, dataset)
		
def get_article_lists(pmids):
	pm_articles = []
	db_articles = []
	for pmid in pmids:
		article = database_interface.get_article(pmid)
		if article is None:
			pm_articles.append(pubmed_interface.PubMedObject(pmid))
		else:
			db_articles.append(article)
	return pm_articles, db_articles

def compute_dataset(titles, abstracts, years_months, pmids, authors):
	distance_matrix = abstract_text.get_abstract_distance_matrix(abstracts)
	
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
			'name' : titles[i], 
			'year': years[i],
			'normYear': norm_years[i],
			'pmid': pmids[i]
		} for i in range(len(titles))], 
		'authors': authors_most_common,
		'distance_matrix': np.around(distance_matrix, decimals=3).tolist(),
		'minYear': {'year': min_year, 'normYear': (min_year - min_pub_time)/range_pub_time},
	'maxYear': {'year': max_year + 1, 'normYear': (max_year + 1 - min_pub_time)/range_pub_time}}

	return dataset