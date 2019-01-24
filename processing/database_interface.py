from database import create_db
from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind=create_db.engine)
from database import models
session = Session()

import datetime
import json
import string

from . import abstract_text

def get_article(pmid):
    """ Returns None if article doesn't exist in database 
    """
    article = session.query(models.Article).filter_by(pmid=pmid).first()
    return article

def save_article(article, abstract_processed, authors):
	try:
		session.add(models.Article(pmid=article.pmid, title=article.title, pub_year=article.pub_year, pub_month=article.pub_month, abstract_processed=abstract_processed, authors=authors))
		session.commit()
	except sqlalchemy.exc.IntegrityError:
		session.rollback()
	except sqlalchemy.exc.SQLAlchemyError as e:
		print('caught sqlalchemy error')
		print(type(e).__name__)

def get_search_term_key(search_term):
	return string.capwords(abstract_text.remove_punctuation(search_term))

def save_dataset(search_term, dataset):
	date = datetime.date.today()
	search_term = get_search_term_key(search_term)
	try:
		session.add(models.SearchTerm(search_term=search_term, dataset=json.dumps(dataset).encode('utf-8'), date_created=date))
		session.commit() 
	except sqlalchemy.exc.IntegrityError:
		session.rollback()
	except sqlalchemy.exc.SQLAlchemyError as e:
		print('caught sqlalchemy error')
		print(type(e).__name__)
