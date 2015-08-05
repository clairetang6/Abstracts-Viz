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
			years_months = data['years_months']

	except:
		print('exception')
		titles, abstracts, years_months = abstract_distance.save_abstracts_and_titles(name, retmax=200)
	
	if len(abstracts) > 0:	
		app.vars['dataset'] = abstract_distance.get_dataset(titles, abstracts, years_months)
		return render_template('viz.html', name=app.vars['name'])
	else:
		return 'No abstracts'
		
 
@app.route("/dataset")
def dataset():
	return json.dumps(app.vars['dataset'])
	 
if __name__ == "__main__":
	app.run(debug=True)
