from flask import Flask, render_template
from datetime import date 
from bs4 import BeautifulSoup

try:
    # For Python 3.0 and later
    from urllib.request import urlopen
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen

app = Flask(__name__)

#Filtered by at least 5 MPG
def category_leader(stats, n, category_index, player_index, mp_index, headers):
	category_list = []
	for i in range(n): 
		#print(i) 
		if stats[0:n][i] is None or len(stats[0:n][i]) == 0:
			category_list.append(0.0)
		else:
			if stats[0:n][i][mp_index] is not None and stats[0:n][i][mp_index] != '' and float(stats[0:n][i][mp_index]) > 10.0:
				category_list.append(float(stats[0:n][i][category_index]))
			else:
				category_list.append(0.0)

	max_val_index = category_list.index(max(category_list))

	leader = stats[0:n][max_val_index][player_index]
	value = max(category_list) 

	return [leader, value]

def run(): 
	#NBA season we will be analyzing
	year = 2020

	#URL page we will be scraping 

	url = "https://www.basketball-reference.com/leagues/NBA_{}_per_game.html".format(year)

	#HTML from given URL 
	html = urlopen(url) 

	soup = BeautifulSoup(html, features='html.parser') 

	#use findAll() to get column headers
	soup.findAll('tr', limit=2) 

	#use getText() to extract the text we need into a list 
	headers = [th.getText() for th in soup.findAll('tr',limit=2)[0].findAll('th')]

	#exclude first column as we won't need ranking order 
	headers = headers[1:]

	#avoid the first header row 
	rows = soup.findAll('tr')[1:]
	player_stats = [[td.getText() for td in rows[i].findAll('td')] for i in range(len(rows))]

	pts_index = headers.index('PTS')
	trb_index = headers.index('TRB')
	ast_index = headers.index('AST')
	player_index = headers.index('Player')
	mp_index = headers.index('MP')

	#Number of players to assess
	n = len(player_stats)

	category = ['PTS', 'TRB', 'AST', 'BLK', 'MP', '3P%', 'FG%']

	#print(stats.head(n))
	leaders = []

	#Assess PPG
	leaders.append(category_leader(player_stats, n, pts_index, player_index, mp_index, headers))

	#Assess RPG
	leaders.append(category_leader(player_stats, n, trb_index, player_index, mp_index, headers))

	#Assess APG
	leaders.append(category_leader(player_stats, n, ast_index, player_index, mp_index, headers))

	#Assess BPG
	#category_leader(stats, n, category[3])

	#Assess MPG
	#category_leader(stats, n, category[4])

	#Assess 3P% Per Game
	#category_leader(stats, n, category[5])

	#Assess FG% Per Game
	#category_leader(stats, n, category[6])

	return leaders 

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
	leader_list = run()
	today = str(date.today()) 
	return render_template('nba.html', date = today, name1 = leader_list[0][0], name2 = leader_list[1][0], name3 = leader_list[2][0], 
		val1 = leader_list[0][1], val2 = leader_list[1][1], val3 = leader_list[2][1])

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