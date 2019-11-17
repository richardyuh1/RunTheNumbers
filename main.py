from flask import Flask, request, render_template
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

#NFL Analysis Functions
def extract_name(th): 
	html_line = str(th)
	sub = "htm"
	sub2 = "</a>"
	index = html_line.find(sub)
	index2 = html_line.find(sub2)
	player_name = html_line[index+5:index2]
	return player_name 

def extract_category(th): 
	html_line = str(th) 
	sub = "ng>" 
	sub2 = "</s"
	index = html_line.find(sub)
	index2 = html_line.find(sub2) 
	category = html_line[index+3:index2]
	return category 

def extract_points(th): 
	html_line = str(th) 
	sub = "</a>"
	index = html_line.find(sub)
	html_updated = html_line[index+5:]
	index2 = html_updated.find(sub) 
	sub2 = "</div>"
	index3 = html_updated.find(sub2)
	val = html_updated[index2+5:index3] 
	final = ""
	for c in val: 
		if c != "(" and c != ")" and c != " ":
			final += c
	return final 

def nfl_run(): 
	#NFL season we will be analyzing
	year = 2020

	#URL page we will be scraping 

	url = "https://www.pro-football-reference.com/leaders/"

	#HTML from given URL 
	html = urlopen(url) 

	soup = BeautifulSoup(html, features='html.parser') 

	th_all = soup.findAll('div', {'class' : 'tabular_row'}, limit = 39)

	#print(th_all)

	player_list = [] 
	category_list = [] 
	points_list = [] 

	for th in th_all:
		player_list.append(extract_name(th))
		category_list.append(extract_category(th))
		points_list.append(extract_points(th))
		#print(th) 


	category_type = ['Passes Completed', 'Passing Yds', 'Passer Rating', 'Passing Yds/Game', 'Pass Completion %', 'Yds/Rushing Att']

	leaders = [] 

	for c in category_type: 
		str_player = player_list[category_list.index(c)]
		str_point = points_list[category_list.index(c)]
		leaders.append([str_player, str_point])

	return leaders 

#NBA Team Standings Functions 
def extract_team_name(link): 
	linkstr = str(link)
	index = linkstr.find("html")
	index2 = linkstr.find("</a>")
	name = linkstr[index+6:index2]
	return name

def extract_team_wins(link): 
	linkstr = str(link)
	index = linkstr.find("wins")
	linkstr_updated = linkstr[index+6:]
	index2 = linkstr_updated.find("</td>")
	name = linkstr_updated[0:index2]
	return name 

def extract_team_losses(link): 
	linkstr = str(link)
	index = linkstr.find("losses")
	linkstr_updated = linkstr[index+8:]
	index2 = linkstr_updated.find("</td>")
	name = linkstr_updated[0:index2]
	return name 

def extract_team_html(all_teams):
	team_list = [] 
	for team in all_teams:
		split_name_list = team.split(" ")
		name = split_name_list[-1]
		team_list.append(name.lower())
	return team_list 

def nba_standings():
	#URL page we will be scraping 

	url = "https://www.basketball-reference.com/leagues/NBA_2020_standings.html"

	#HTML from given URL 
	html = urlopen(url) 

	soup = BeautifulSoup(html, features='html.parser') 

	#th_all = soup.findAll('a', {'class' : 'AnchorLink'}, limit = 100)
	th_all = soup.findAll('tr', {'class' : 'full_table'}, limit = 30)

	east_teams_raw = th_all[0:15] 
	west_teams_raw = th_all[15:30]

	east_standings = [] 
	east_wins = [] 
	east_losses = []
	west_standings = [] 
	west_wins = [] 
	west_losses = [] 
	all_teams = [] 

	for link in east_teams_raw:
		east_standings.append(extract_team_name(link))
		east_wins.append(extract_team_wins(link))
		east_losses.append(extract_team_losses(link))

	for link in west_teams_raw:
		west_standings.append(extract_team_name(link))
		west_wins.append(extract_team_wins(link))
		west_losses.append(extract_team_losses(link))

	east_standings_copy = east_standings.copy() 
	east_standings_copy.extend(west_standings) 
	all_teams = extract_team_html(east_standings_copy) 

	return [east_standings, east_wins, east_losses, west_standings, west_wins, west_losses, all_teams] 

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

#Rockets Page 
@app.route('/rockets')
def rockets(): 
	return render_template('rockets.html')

#Lakers Page
@app.route('/lakers')
def lakers():
	return render_template('lakers.html')

#Nets Page
@app.route('/nets')
def nets():
	return render_template('nets.html')

#Pistons Page
@app.route('/pistons')
def pistons():
	return render_template('pistons.html')

#Celtics Page
@app.route('/celtics')
def celtics(): 
	return render_template('celtics.html')

#Magic Page
@app.route('/magic')
def magic(): 
	return render_template('magic.html') 

#NBA Team Index 
@app.route('/nbateams')
def nbateams(): 
	return render_template('nbateams.html')

#NFL Team Index 
@app.route('/nflteams')
def nflteams(): 
	return render_template('nflteams.html')

#NBA Team Standings 
@app.route('/nbateamstandings')
def nbateamstandings(): 
	standings = nba_standings() 
	east_standings = standings[0]
	east_wins = standings[1] 
	east_losses = standings[2] 
	west_standings = standings[3]
	west_wins = standings[4] 
	west_losses = standings[5] 
	east_teams = standings[6][0:15]
	west_teams = standings[6][15:30]
	return render_template('nbateamstandings.html', eaststandings = east_standings, weststandings = west_standings, eastteams = east_teams, 
		westteams = west_teams, eastwins = east_wins, eastlosses = east_losses, westwins = west_wins, westlosses = west_losses) 

#NFL Team Index
@app.route('/nflteamstandings')
def nflteamstandings(): 
	return render_template('nflteamstandings.html')
	
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
	leader_list = nfl_run() 
	today = str(date.today())
	return render_template('nfl.html', date = today, name1 = leader_list[0][0], name2 = leader_list[1][0], name3 = leader_list[2][0], 
		name4 = leader_list[3][0], name5 = leader_list[4][0], name6 = leader_list[5][0], val1 = leader_list[0][1], val2 = leader_list[1][1], 
		val3 = leader_list[2][1], val4 = leader_list[3][1], val5 = leader_list[4][1], val6 = leader_list[5][1])

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