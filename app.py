import asyncio
from aiohttp import web
from processing import abstract_distance
import json

app = web.Application()
app.vars = {}
my_request = {}

@asyncio.coroutine
def input_form(request):
	print(request)
	with open('templates/form.html', 'r') as f:
		html = f.read()
	return web.Response(body=html.encode('utf-8'))
app.router.add_route("GET", "/", input_form)

@asyncio.coroutine
def output(request):
	data = yield from request.content.read()
	print(data)
	app.vars['name'] = data['scientist_name']
	name = app.vars['name']
	print(name)
#	
#	try:
#		with open('%s.txt'%name.replace(' ', '') , 'r') as f:
#			data = json.load(f)
#			titles = data['titles']

#			abstracts = data['abstracts']
#			years_months = data['years_months']
#			pmids = data['pmids']

#	except:
#		print('no data for ' + name + ', getting abstracts now')
#		titles, abstracts, years_months, pmids = abstract_distance.save_abstracts_and_titles(name, retmax=200)
	
#	if len(abstracts) > 0:	
#		app.vars['dataset'] = abstract_distance.get_dataset(titles, abstracts, years_months, pmids)
#		return render_template('viz.html', name=app.vars['name'])
#	else:
#		return 'No abstracts'
app.router.add_route("POST", "/index", output)	
 
#@app.route("/dataset")
#def dataset():
#	return json.dumps(app.vars['dataset'])
	 
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