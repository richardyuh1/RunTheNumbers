from flask import Flask, render_template
#from data import Articles

app = Flask(__name__)

#Index
@app.route('/')
def index():
	return render_template('home.html')

#About
@app.route('/about')
def about():
	return render_template('about.html')



if __name__ == '__main__':
	app.secret_key='secret123'
	app.run(debug=True)