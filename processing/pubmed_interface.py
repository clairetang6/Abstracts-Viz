# -*- coding: utf-8 -*-
"""
Created on Sun Jul 26 18:45:35 2015

@author: Claire Tang
"""
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import time 
import os

api_key = os.environ['PUBMED_API_KEY']

class PubMedObject:    
    month_dict = {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6, 'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12}
    
    def __init__(self, pmid):
        self.pmid = pmid.strip()
        self.pubmed_url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=' + self.pmid + '&api_key=' + str(api_key) + '&retmode=xml&rettype=abstract'
        self.html_file = ''
        self.title = ''
        self.journal = ''
        self.abstract = ''
        self.pub_year = ''
        self.pub_month = ''
        self.authors = []
    
    async def download(self, session=None):
        if session is None:
            async with aiohttp.ClientSession() as session:
                session = RateLimiter(session)
                await self.download_with_session(session)
        else:
            await self.download_with_session(session)

    async def download_with_session(self, session):
        status = 500
        while status != 200:
            try:
                async with await session.get(self.pubmed_url) as response:
                    status = response.status
                    if status == 200:
                        self.html_file = await response.text()
            except Exception as e:
                print(type(e).__name__)

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
                if soup.find('PubDate').Month.string.strip() in PubMedObject.month_dict.keys():
                    self.pub_month = PubMedObject.month_dict[soup.find('PubDate').Month.string.strip()]
                else:
                    self.pub_month = 6
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

sem = asyncio.Semaphore(2)

async def download_articles(articles):
    with (await sem):
        session = get_client_session()
        tasks = [download_article(article, session) for article in articles]
        await asyncio.gather(*tasks)
    await session.close()

async def download_article(article, session=None):
    await article.download(session)
                
def get_client_session():
    """ returned session must be closed after use
    """
    connector = aiohttp.TCPConnector(limit=10)
    return RateLimiter(aiohttp.ClientSession(connector=connector))

class RateLimiter:
    RATE = 5
    MAX_TOKENS = 5

    def __init__(self, session):
        self.session = session
        self.tokens = self.MAX_TOKENS
        self.updated_at = time.monotonic()

    async def get(self, *args, **kwargs):
        await self.wait_for_token()
        return self.session.get(*args, **kwargs)

    async def wait_for_token(self):
        while self.tokens <= 1:
            self.add_new_tokens()
            await asyncio.sleep(1)
        self.tokens = self.tokens - 1
    
    def add_new_tokens(self):
        now = time.monotonic()
        time_since_update = now - self.updated_at
        new_tokens = time_since_update * self.RATE
        if self.tokens + new_tokens >= 1:
            self.tokens = min(self.tokens + new_tokens, self.MAX_TOKENS)
            self.updated_at = now

    async def close(self):
        await self.session.close()

async def search_pubmed(term, search_author=False, retmax=250):
    if search_author:
        print('search pubmed author: ' + term)
        term = term + '[Full Author Name]'
    else:
        print('search pubmed term: ' + term)
    payload = {'db': 'pubmed', 'retmode': 'json', 'term': term, 'retmax': retmax}
    pubmed_search_url = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi'
    async with aiohttp.ClientSession() as session:
        async with session.get(pubmed_search_url, params=payload) as response:
            response_json = await response.json()
    return [pmid for pmid in response_json['esearchresult']['idlist']]
