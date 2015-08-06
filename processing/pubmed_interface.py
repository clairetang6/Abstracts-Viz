# -*- coding: utf-8 -*-
"""
Created on Sun Jul 26 18:45:35 2015

@author: Claire Tang
"""
import urllib
from bs4 import BeautifulSoup

class PubMedObject:    
    month_dict = {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6, 'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12}
    
    def __init__(self, pmid):
        self.pmid = pmid.strip()
        self.pubmed_url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=' + self.pmid + '&retmode=xml&rettype=abstract'
        self.html_file = ''
        self.title = ''
        self.journal = ''
        self.abstract = ''
        self.pub_year = ''
        self.pub_month = ''
        
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
            if soup.find('PubDate').Year:
                self.pub_year = soup.find('PubDate').Year.string
            if soup.find('PubDate').Month:
                self.pub_month = PubMedObject.month_dict[soup.find('PubDate').Month.string.strip()]
            else:
                self.pub_month = 6
            
import requests
import json

def search_pubmed(term, retmax=250):
    payload = {'db': 'pubmed', 'retmode': 'json', 'term': term, 'retmax': retmax}
    r = requests.get('http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi', payload)
    return [pmid for pmid in json.loads(r.text)['esearchresult']['idlist']]

def search_pubmed_author(author, retmax=250):
    return search_pubmed(author + '[Full Author Name]', retmax=retmax)
    
    
        