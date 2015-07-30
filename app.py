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
			titles = data['titles']
			abstracts = data['abstracts']
			years = data['years']

	except:
		print('exception')
		titles, abstracts, years = abstract_distance.save_abstracts_and_titles(name)
	
	if len(abstracts) > 0:	
		app.vars['dataset'] = abstract_distance.get_dataset(titles, abstracts, years)
		return render_template('viz.html')
	else:
		return 'No abstracts'
		
 
@app.route("/dataset")
def dataset():
	return json.dumps(app.vars['dataset'])
	 
if __name__ == "__main__":
	app.run(debug=True)
