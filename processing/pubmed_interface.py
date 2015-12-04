# -*- coding: utf-8 -*-
"""
Created on Sun Jul 26 18:45:35 2015

@author: Claire Tang
"""
import asyncio
import aiohttp
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
        self.authors = []
        
    async def download(self, session=None):
        if session is not None:
            get = session.get
        else:
            get = aiohttp.get
        status = 500
        response = await get(self.pubmed_url)
        status = response.status 
        while status != 200:    
            await response.release()
            response = await get(self.pubmed_url)
            status = response.status
        self.html_file = await response.text()
        await response.release()
        
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
        if soup.find('AuthorList'):
            authors = soup.find('AuthorList').find_all('Author')
            for author in authors:
                first_name = author.find('ForeName')
                last_name = author.find('LastName')
                first_name = '' if not first_name else first_name.string
                last_name = '' if not last_name else last_name.string
                self.authors.append(first_name + ' ' + last_name)
                
async def download_articles(articles):
    with aiohttp.ClientSession() as client:
        tasks = [download_article(article, client) for article in articles]
        await asyncio.gather(*tasks)

async def download_article(article, session=None):
    await article.download(session)
            
import json

async def search_pubmed(term, search_author=False, retmax=250):
    if search_author:
        print('search pubmed author: ' + term)
        term = term + '[Full Author Name]'
    else:
        print('search pubmed term: ' + term)
    payload = {'db': 'pubmed', 'retmode': 'json', 'term': term, 'retmax': retmax}
    response = await aiohttp.get('http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi', params=payload)
    response_text = await response.text()
    await response.release()
    return [pmid for pmid in json.loads(response_text)['esearchresult']['idlist']]
    
        