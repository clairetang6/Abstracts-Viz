from app import db

class Scientist(db.Model):
	name = db.Column(db.String(), primary_key=True)
	dataset = db.Column(db.LargeBinary())
	
	def __init__(self, name, dataset=None):
		self.name = name
		self.dataset = dataset
	
	def __repr__(self):
		return '<Scientist {0}>'.format(self.name)
		
class Article(db.Model):
	pmid = db.Column(db.Integer(), primary_key=True)
	title = db.Column(db.String())
	pub_year = db.Column(db.Integer())
	pub_month = db.Column(db.Integer())
	abstract_processed = db.Column(db.LargeBinary())
	
	def __init__(self, pmid, title, pub_year, pub_month, abstract_processed):
		self.pmid = pmid
		self.title = title
		self.pub_year = pub_year
		self.pub_month = pub_month
		self.abstract_processed = abstract_processed
		
	def __repr__(self):
		return '<Article {0}: {1}>'.format(self.pmid, self.title[:20])
		
	
