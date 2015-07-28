from flask import Flask
from flask import render_template
from flask import request
from processing import abstract_distance
import json

app = Flask(__name__)
app.vars = {}

@app.route("/")
def input_form():
	return render_template('form.html')

@app.route("/index", methods=['POST'])
def output():
	app.vars['name'] = request.form['scientist_name']
	name = app.vars['name']
	
	try:
		with open('%s.txt'%name.replace(' ', '') , 'r') as f:
			data = json.load(f)
			print(data.keys())
			app.vars['dataset'] = abstract_distance.get_dataset(data['titles'], data['abstracts'])
	except:
		print('exception')
		titles, abstracts = abstract_distance.save_abstracts_and_titles(name)
		app.vars['dataset'] = abstract_distance.get_dataset(titles, abstracts)
	finally:	
		return render_template('viz.html')
 
@app.route("/dataset")
def dataset():
	return json.dumps(app.vars['dataset'])
	 
if __name__ == "__main__":
	app.run(debug=True)
