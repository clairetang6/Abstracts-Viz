from flask import Flask
from flask import render_template
from flask import request

app = Flask(__name__)
app.vars = {}

@app.route("/")
def input_form():
	return render_template('form.html')

@app.route("/index", methods=['POST'])
def output():
	app.vars['name'] = request.form['scientist_name']
	
	with open('%s.text'%(app.vars['name']), 'w') as f:
		f.write("Name : %s\n"%(app.vars['name']))
		
	return 'Posted data'

if __name__ == "__main__":
	app.run(debug=True)
