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

#Articles 
@app.route('/articles')
def articles():
	return render_template('articles.html')

#Nba
@app.route('/nba')
def nba():
	return render_template('nba.html')

#Nfl
@app.route('/nfl')
def nfl():
	return render_template('nfl.html')

#Register
@app.route('/register')
def register():
	return render_template('register.html')

#Login
@app.route('/login')
def login():
	return render_template('login.html')


if __name__ == '__main__':
	app.secret_key='secret123'
	app.run(debug=True)