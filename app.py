import asyncio
from aiohttp import web
import json
from processing import abstract_distance
from database import create_db
from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind=create_db.engine)
from database import models

app = web.Application()


@asyncio.coroutine
def input_form(request):
	with open('templates/form.html', 'r') as f:
		html = f.read()
	return web.Response(body=html.encode('utf-8'))
app.router.add_route("GET", "/", input_form)

@asyncio.coroutine
def output(request):
	data = yield from request.content.read()
	name = data.decode('utf-8').replace('+',' ').partition('scientist_name=')[2]
	web_response = yield from asyncio.async(send_response_name(name))
	yield from get_abstracts(name)

	return web_response
app.router.add_route("POST", "/index", output)	

@asyncio.coroutine
def get_abstracts(name):
	print('getting abstracts')
	session = Session()
	scientist = session.query(models.Scientist).filter_by(name=name).first()
	session.close()
	if scientist:
		return
	else:
		print('no data for ' + name + ', getting abstracts now')
		asyncio.Task(abstract_distance.save_abstracts_and_titles(name, 200))

@asyncio.coroutine	
def send_response_name(name):
	with open('templates/viz.html', 'r') as f:
		html = f.read()
	html = html.replace("{{ name }}", name)
	return web.Response(body=html.encode('utf-8'))
	

@asyncio.coroutine 
def dataset(request):
	name = request.match_info['name']
	session = Session()
	scientist = session.query(models.Scientist).filter_by(name=name).first()
	if scientist:
		return web.Response(body=scientist.dataset, content_type='text/json')
	else:
		return web.HTTPBadRequest()
		
app.router.add_route("GET", "/dataset/{name}", dataset)

app.router.add_static("/static", "static/")
	 
if __name__ == "__main__":
	loop = asyncio.get_event_loop()
	handler = app.make_handler()
	f = loop.create_server(handler, '0.0.0.0', 5000)
	server = loop.run_until_complete(f)
	print('serving on ', server.sockets[0].getsockname())
	try: 
		loop.run_forever()
	except KeyboardInterrupt:
		pass
	finally:
		loop.run_until_complete(handler.finish_connections(1.0))
		server.close()
		loop.run_until_complete(server.wait_closed())
		loop.run_until_complete(app.finish())
	loop.close()