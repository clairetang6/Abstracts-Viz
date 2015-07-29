# -*- coding: utf-8 -*-
"""
Created on Sun Jul 26 18:45:35 2015

@author: Claire Tang
"""
import urllib
from bs4 import BeautifulSoup

class PubMedObject:
    doi = ''
    pubmed_url = ''
    html_file = ''
    
    title = ''
    journal = ''
    abstract = ''
    pub_year = ''
    
    def __init__(self, doi):
        self.doi = doi.strip()
        self.pubmed_url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=' + self.doi + '&retmode=xml&rettype=abstract'
        
    def download(self):
        response = urllib.request.urlopen(urllib.request.Request(self.pubmed_url))
        try: 
            self.html_file = response.read()
        except: 
            print('error reading response from pubmed url');
        response.close()
        
    def fill_data(self):
        soup = BeautifulSoup(self.html_file, 'xml')
        
        if soup.find('ArticleTitle'):
            self.title = soup.find('ArticleTitle').string
        if soup.find('Journal'):
            self.journal = soup.find('Journal').Title.string
        if soup.find('AbstractText'):
            self.abstract = soup.find('AbstractText').string
        if soup.find('PubDate'):
            self.pub_year = soup.find('PubDate').Year.string
            
import requests
import json

def search_pubmed(term, retmax=250):
    payload = {'db': 'pubmed', 'retmode': 'json', 'term': term, 'retmax': retmax}
    r = requests.get('http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi', payload)
    return [doi for doi in json.loads(r.text)['esearchresult']['idlist']]

def search_pubmed_author(author, retmax=250):
    return search_pubmed(author + '[Full Author Name]', retmax=retmax)
    
    
        