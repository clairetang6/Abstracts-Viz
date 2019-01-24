import asyncio
from aiohttp import web
import aiohttp_jinja2
import jinja2
from processing import backend
from processing import database_interface
from database import create_db
from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind=create_db.engine)
from database import models

app = web.Application()
aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('templates/'))


async def input_form(request):
	with open('templates/form.html', 'r') as f:
		html = f.read()
	return web.Response(body=html.encode('utf-8'), content_type="text/html")
app.add_routes([web.get("/", input_form)])

async def output(request):
	data = await request.content.read()
	name = data.decode('utf-8').replace('+',' ').partition('scientist_name=')[2]
	response = aiohttp_jinja2.render_template('viz.html', request, {'name': name})
	await get_abstracts(name)

	return response
app.add_routes([web.post("/index", output)])	

async def get_abstracts(search_term):
	print('getting abstracts')
	session = Session()
	search_term = database_interface.get_search_term_key(search_term)
	try:
		searched_term = session.query(models.SearchTerm).filter_by(search_term=search_term).first()
	except Exception as e:
		print(type(e).__name__)
	finally:
		session.close()
	if searched_term:
		return
	else:
		print('no data for ' + search_term + ', getting abstracts now')
		asyncio.ensure_future(backend.search_pubmed_save_articles_compute_distance_dataset(search_term, 100))

async def dataset(request):
	search_term = request.match_info['name']
	session = Session()
	search_term = database_interface.get_search_term_key(search_term)
	try:
		searched_term = session.query(models.SearchTerm).filter_by(search_term=search_term).first()	
	except Exception as e:
		print(type(e).__name__)
	finally:
		session.close()
	if searched_term:
		return web.Response(body=searched_term.dataset, content_type='text/json')
	else:
		return web.HTTPAccepted()
		
app.add_routes([web.get("/dataset/{name}", dataset)])

app.add_routes([web.static("/static", "static/")])
	 
if __name__ == "__main__":
	web.run_app(app)