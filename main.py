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

#Filtered by at least 10 MPG and at least 5 games played 
def category_leader(stats, n, category_index, player_index, mp_index, game_index, headers):
	category_list = []
	for i in range(n): 
		if stats[0:n][i] is None or len(stats[0:n][i]) == 0 or len(stats[0:n][i][category_index]) == 0:
			category_list.append(0.0)
		else:
			if stats[0:n][i][mp_index] is not None and stats[0:n][i][mp_index] != '' and float(stats[0:n][i][mp_index]) > 10.0:
				if stats[0:n][i][game_index] is not None and stats[0:n][i][game_index] != '' and float(stats[0:n][i][game_index]) > 4.0:
					category_list.append(float(stats[0:n][i][category_index]))
				else:
					category_list.append(0.0)
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

	'''
	['Player', 'Pos', 'Age', 'Tm', 'G', 'GS', 'MP', 'FG', 'FGA', 'FG%', '3P', 
	'3PA', '3P%', '2P', '2PA', '2P%', 'eFG%', 'FT', 'FTA', 'FT%', 'ORB', 'DRB', 
	'TRB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS']
	'''
	player_index = headers.index('Player')
	pos_index = headers.index('Pos')
	age_index = headers.index('Age')
	trey_percent_index = headers.index('3P%')
	fg_percent_index = headers.index('FG%')
	mp_index = headers.index('MP')
	trb_index = headers.index('TRB')
	ast_index = headers.index('AST')
	stl_index = headers.index('STL')
	blk_index = headers.index('BLK')
	tov_index = headers.index('TOV')
	pf_index = headers.index('PF')
	pts_index = headers.index('PTS')
	game_index = headers.index('G')

	#Number of players to assess
	n = len(player_stats)

	#print(stats.head(n))
	leaders = []

	#Assess PPG
	leaders.append(category_leader(player_stats, n, pts_index, player_index, mp_index, game_index, headers))

	#Assess RPG
	leaders.append(category_leader(player_stats, n, trb_index, player_index, mp_index, game_index, headers))

	#Assess APG
	leaders.append(category_leader(player_stats, n, ast_index, player_index, mp_index, game_index, headers))

	#Assess BPG
	leaders.append(category_leader(player_stats, n, blk_index, player_index, mp_index, game_index, headers))

	#Assess MPG
	#leaders.append(category_leader(player_stats, n, mp_index, player_index, mp_index, headers))

	#Assess 3P% Per Game
	leaders.append(category_leader(player_stats, n, trey_percent_index, player_index, mp_index, game_index, headers))

	#Assess FG% Per Game
	leaders.append(category_leader(player_stats, n, fg_percent_index, player_index, mp_index, game_index, headers))

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
		name4 = leader_list[3][0], name5 = leader_list[4][0], name6 = leader_list[5][0], val1 = leader_list[0][1], val2 = leader_list[1][1], 
		val3 = leader_list[2][1], val4 = leader_list[3][1], val5 = leader_list[4][1], val6 = leader_list[5][1])

#Nfl
@app.route('/nfl')
def nfl():
	today = str(date.today())
	return render_template('nfl.html', date = today)

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