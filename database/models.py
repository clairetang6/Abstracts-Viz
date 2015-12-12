from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, LargeBinary, Date

Base = declarative_base()

class SearchTerm(Base):
	__tablename__ = 'search_terms'
	
	search_term = Column(String, primary_key=True)
	dataset = Column(LargeBinary)
	date_created = Column(Date)
	
	def __repr__(self):
		return "<Search Term: {0}, {1}>".format(self.search_term, self.date_created)
		
class Article(Base):
	__tablename__ ='articles'
	
	pmid = Column(Integer, primary_key=True)
	title = Column(String)
	pub_year = Column(Integer)
	pub_month = Column(Integer)
	abstract_processed = Column(LargeBinary)
	authors = Column(LargeBinary)
	
	def __repr__(self):
		return '<Article {0}: {1}'.format(self.pmid, self.title)
	