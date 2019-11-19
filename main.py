from flask import Flask, request, render_template, redirect 
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

def extract_nba_seed(link):
	linkstr = str(link)
	index = linkstr.find("seed")
	index2 = linkstr[index:].find(")")
	seed = linkstr[index+7:index+index2]
	return seed 

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
	east_seed = []
	west_seed = [] 

	for link in east_teams_raw:
		east_standings.append(extract_team_name(link))
		east_wins.append(extract_team_wins(link))
		east_losses.append(extract_team_losses(link))
		east_seed.append(extract_nba_seed(link))

	for link in west_teams_raw:
		west_standings.append(extract_team_name(link))
		west_wins.append(extract_team_wins(link))
		west_losses.append(extract_team_losses(link))
		west_seed.append(extract_nba_seed(link))

	east_standings_copy = east_standings[:]
	east_standings_copy.extend(west_standings) 
	all_teams = extract_team_html(east_standings_copy) 

	return [east_standings, east_wins, east_losses, west_standings, west_wins, west_losses, all_teams, east_seed, west_seed] 

#NFL Team Standings 
def extract_nfl_page(name):
	arr = name.split(" ")
	return arr[-1].lower()

def extract_nfl_name(th): 
	index = th.find("htm")
	index2 = th.find("</a")
	teamname = th[index+5:index2]
	index3 = th.find("wins")
	index4 = th[index3:].find("</td>")
	wins = th[index3+6:index3+index4]
	index5 = th.find("losses")
	index6 = th[index5:].find("</td>")
	losses = th[index5+8:index5+index6]
	page = extract_nfl_page(teamname)
	return [teamname, wins, losses, page]

def nfl_standings():

	#URL page we will be scraping 
	url = "https://www.pro-football-reference.com/years/2019/index.htm"

	#HTML from given URL 
	html = urlopen(url) 

	soup = BeautifulSoup(html, features='html.parser') 

	th_all = soup.findAll('tr', limit = 42)
	th_all = th_all[1:]

	#Grouped by 5s 
	#Remove 0, 5, 10, 15, 20, 21, 26, 31, 36

	th_all[0] = None 
	th_all[5] = None 
	th_all[10] = None
	th_all[15] = None
	th_all[20] = None
	th_all[21] = None
	th_all[26] = None 
	th_all[31] = None
	th_all[36] = None 

	team_list = [] 

	for th in th_all:
		if th is not None:
			team_list.append(extract_nfl_name(str(th)))
	
	return team_list

##############   NBA Team Roster Automated    ################
def calculateAge(birthDate): 
    today = date.today() 
    age = today.year - birthDate.year - ((today.month, today.day) < (birthDate.month, birthDate.day)) 
  
    return age 

def extract_roster_name(th):
	th = str(th)
	index = th.find("html")
	index2 = th[index:].find("</a>")
	return th[index+6:index+index2]

def extract_roster_position(th):
	th = str(th)
	index = th.find("pos")
	index2 = th[index:].find("</td>")
	return th[index+5:index+index2]

def extract_roster_height(th):
	th = str(th)
	index = th.find("height")
	index2 = th[index:].find("</td>")
	return th[index+8:index+index2]

def extract_roster_weight(th):
	th = str(th)
	index = th.find("weight")
	index2 = th[index:].find("</td>")
	return th[index+8:index+index2]

def extract_roster_season(th):
	th = str(th)
	index = th.find("experience")
	index2 = th[index:].find("</td>")
	str_exp = th[index+12:index+index2]
	if str_exp == 'R':
		return 1 
	exp = int(th[index+12:index+index2])
	return str(exp+1)

def extract_roster_college(th):
	th = str(th)
	college_index = th.find("colleges")
	if college_index == -1:
		return '' 
	index = th[college_index:].find(">")
	index2 = th[college_index+index+1:].find("<")
	college_name_raw = th[college_index+index+1:college_index+index+1+index2]
	#Remove &/amp;
	college_name_list = college_name_raw.split(" ")
	for i,name in enumerate(college_name_list):
		if 'amp;' in name:
			index = name.find('amp;')
			college_name_list[i] = name[0:index] + name[index+4:]
	return " ".join(college_name_list)

#year, month, day in int form 
def extract_roster_age(th):
	months = {'January':1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6, 'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12}

	th = str(th)
	age_index = th.find("date")
	index2 = th[age_index:].find("</td")
	birthdatestr = th[age_index+6:age_index+index2]
	birthdaysplit = birthdatestr.split(' ')
	month = months[birthdaysplit[0]]
	day = int(birthdaysplit[1][0:-1])
	year = int(birthdaysplit[2])
	return calculateAge(date(year, month, day))

def lakers_roster_automate():
	year = 2020

	#URL page we will be scraping 

	url = "https://www.basketball-reference.com/teams/LAL/{}.html".format(year)

	#HTML from given URL 
	html = urlopen(url) 

	soup = BeautifulSoup(html, features='html.parser') 

	#use findAll() to get column headers
	th_all = soup.findAll('tr', limit=19) 
	th_all = th_all[1:]

	player_name = [] 
	player_pos = [] 
	player_height = []
	player_weight = [] 
	player_season = [] 
	player_college = []
	player_age = [] 

	for th in th_all:
		player_name.append(extract_roster_name(th))
		player_pos.append(extract_roster_position(th))
		player_height.append(extract_roster_height(th))
		player_weight.append(extract_roster_weight(th))
		player_season.append(extract_roster_season(th))
		player_college.append(extract_roster_college(th))
		player_age.append(extract_roster_age(th))

	final = [player_name, player_pos, player_height, player_weight, player_season, player_college, player_age]
	return final 

def rockets_roster_automate():
	year = 2020

	#URL page we will be scraping 

	url = "https://www.basketball-reference.com/teams/HOU/{}.html".format(year)

	#HTML from given URL 
	html = urlopen(url) 

	soup = BeautifulSoup(html, features='html.parser') 

	#use findAll() to get column headers
	th_all = soup.findAll('tr', limit=19) 
	th_all = th_all[1:]

	player_name = [] 
	player_pos = [] 
	player_height = []
	player_weight = [] 
	player_season = [] 
	player_college = []
	player_age = [] 

	for th in th_all:
		player_name.append(extract_roster_name(th))
		player_pos.append(extract_roster_position(th))
		player_height.append(extract_roster_height(th))
		player_weight.append(extract_roster_weight(th))
		player_season.append(extract_roster_season(th))
		player_college.append(extract_roster_college(th))
		player_age.append(extract_roster_age(th))

	player_name[13] = Nene

	final = [player_name, player_pos, player_height, player_weight, player_season, player_college, player_age]
	return final 

def celtics_roster_automate():
	year = 2020

	#URL page we will be scraping 

	url = "https://www.basketball-reference.com/teams/BOS/{}.html".format(year)

	#HTML from given URL 
	html = urlopen(url) 

	soup = BeautifulSoup(html, features='html.parser') 

	#use findAll() to get column headers
	th_all = soup.findAll('tr', limit=19) 
	th_all = th_all[1:]

	player_name = [] 
	player_pos = [] 
	player_height = []
	player_weight = [] 
	player_season = [] 
	player_college = []
	player_age = [] 

	for th in th_all:
		player_name.append(extract_roster_name(th))
		player_pos.append(extract_roster_position(th))
		player_height.append(extract_roster_height(th))
		player_weight.append(extract_roster_weight(th))
		player_season.append(extract_roster_season(th))
		player_college.append(extract_roster_college(th))
		player_age.append(extract_roster_age(th))

	final = [player_name, player_pos, player_height, player_weight, player_season, player_college, player_age]
	return final 

def magic_roster_automate():
	year = 2020

	#URL page we will be scraping 

	url = "https://www.basketball-reference.com/teams/ORL/{}.html".format(year)

	#HTML from given URL 
	html = urlopen(url) 

	soup = BeautifulSoup(html, features='html.parser') 

	#use findAll() to get column headers
	th_all = soup.findAll('tr', limit=19) 
	th_all = th_all[1:]

	player_name = [] 
	player_pos = [] 
	player_height = []
	player_weight = [] 
	player_season = [] 
	player_college = []
	player_age = [] 

	for th in th_all:
		player_name.append(extract_roster_name(th))
		player_pos.append(extract_roster_position(th))
		player_height.append(extract_roster_height(th))
		player_weight.append(extract_roster_weight(th))
		player_season.append(extract_roster_season(th))
		player_college.append(extract_roster_college(th))
		player_age.append(extract_roster_age(th))

	player_name[9] = 'Nikola Vucevic'
	final = [player_name, player_pos, player_height, player_weight, player_season, player_college, player_age]
	return final 

def nets_roster_automate():
	year = 2020

	#URL page we will be scraping 

	url = "https://www.basketball-reference.com/teams/BRK/{}.html".format(year)

	#HTML from given URL 
	html = urlopen(url) 

	soup = BeautifulSoup(html, features='html.parser') 

	#use findAll() to get column headers
	th_all = soup.findAll('tr', limit=19) 
	th_all = th_all[1:]

	player_name = [] 
	player_pos = [] 
	player_height = []
	player_weight = [] 
	player_season = [] 
	player_college = []
	player_age = [] 

	for th in th_all:
		player_name.append(extract_roster_name(th))
		player_pos.append(extract_roster_position(th))
		player_height.append(extract_roster_height(th))
		player_weight.append(extract_roster_weight(th))
		player_season.append(extract_roster_season(th))
		player_college.append(extract_roster_college(th))
		player_age.append(extract_roster_age(th))

	# Fix names 
	player_name[3] = 'Dzanan Musa'
	player_name[16] = 'Timothe Luwawu-Cabarrot'

	final = [player_name, player_pos, player_height, player_weight, player_season, player_college, player_age]
	return final 

def pistons_roster_automate():
	year = 2020

	#URL page we will be scraping 

	url = "https://www.basketball-reference.com/teams/DET/{}.html".format(year)

	#HTML from given URL 
	html = urlopen(url) 

	soup = BeautifulSoup(html, features='html.parser') 

	#use findAll() to get column headers
	th_all = soup.findAll('tr', limit=19) 
	th_all = th_all[1:]

	player_name = [] 
	player_pos = [] 
	player_height = []
	player_weight = [] 
	player_season = [] 
	player_college = []
	player_age = [] 

	for th in th_all:
		player_name.append(extract_roster_name(th))
		player_pos.append(extract_roster_position(th))
		player_height.append(extract_roster_height(th))
		player_weight.append(extract_roster_weight(th))
		player_season.append(extract_roster_season(th))
		player_college.append(extract_roster_college(th))
		player_age.append(extract_roster_age(th))

	final = [player_name, player_pos, player_height, player_weight, player_season, player_college, player_age]
	return final 

def warriors_roster_automate():
	year = 2020

	#URL page we will be scraping 

	url = "https://www.basketball-reference.com/teams/GSW/{}.html".format(year)

	#HTML from given URL 
	html = urlopen(url) 

	soup = BeautifulSoup(html, features='html.parser') 

	#use findAll() to get column headers
	th_all = soup.findAll('tr', limit=19) 
	th_all = th_all[1:]

	player_name = [] 
	player_pos = [] 
	player_height = []
	player_weight = [] 
	player_season = [] 
	player_college = []
	player_age = [] 

	player_name[5] = 'Alen Smailagic'

	for th in th_all:
		player_name.append(extract_roster_name(th))
		player_pos.append(extract_roster_position(th))
		player_height.append(extract_roster_height(th))
		player_weight.append(extract_roster_weight(th))
		player_season.append(extract_roster_season(th))
		player_college.append(extract_roster_college(th))
		player_age.append(extract_roster_age(th))

	final = [player_name, player_pos, player_height, player_weight, player_season, player_college, player_age]
	return final 

def knicks_roster_automate():
	year = 2020

	#URL page we will be scraping 

	url = "https://www.basketball-reference.com/teams/NYK/{}.html".format(year)

	#HTML from given URL 
	html = urlopen(url) 

	soup = BeautifulSoup(html, features='html.parser') 

	#use findAll() to get column headers
	th_all = soup.findAll('tr', limit=19) 
	th_all = th_all[1:]

	player_name = [] 
	player_pos = [] 
	player_height = []
	player_weight = [] 
	player_season = [] 
	player_college = []
	player_age = [] 

	for th in th_all:
		player_name.append(extract_roster_name(th))
		player_pos.append(extract_roster_position(th))
		player_height.append(extract_roster_height(th))
		player_weight.append(extract_roster_weight(th))
		player_season.append(extract_roster_season(th))
		player_college.append(extract_roster_college(th))
		player_age.append(extract_roster_age(th))

	final = [player_name, player_pos, player_height, player_weight, player_season, player_college, player_age]
	return final 

def clippers_roster_automate():
	year = 2020

	#URL page we will be scraping 

	url = "https://www.basketball-reference.com/teams/LAC/{}.html".format(year)

	#HTML from given URL 
	html = urlopen(url) 

	soup = BeautifulSoup(html, features='html.parser') 

	#use findAll() to get column headers
	th_all = soup.findAll('tr', limit=19) 
	th_all = th_all[1:]

	player_name = [] 
	player_pos = [] 
	player_height = []
	player_weight = [] 
	player_season = [] 
	player_college = []
	player_age = [] 

	for th in th_all:
		player_name.append(extract_roster_name(th))
		player_pos.append(extract_roster_position(th))
		player_height.append(extract_roster_height(th))
		player_weight.append(extract_roster_weight(th))
		player_season.append(extract_roster_season(th))
		player_college.append(extract_roster_college(th))
		player_age.append(extract_roster_age(th))

	final = [player_name, player_pos, player_height, player_weight, player_season, player_college, player_age]
	return final 

def grizzlies_roster_automate():
	year = 2020

	#URL page we will be scraping 

	url = "https://www.basketball-reference.com/teams/MEM/{}.html".format(year)

	#HTML from given URL 
	html = urlopen(url) 

	soup = BeautifulSoup(html, features='html.parser') 

	#use findAll() to get column headers
	th_all = soup.findAll('tr', limit=19) 
	th_all = th_all[1:]

	player_name = [] 
	player_pos = [] 
	player_height = []
	player_weight = [] 
	player_season = [] 
	player_college = []
	player_age = [] 

	for th in th_all:
		player_name.append(extract_roster_name(th))
		player_pos.append(extract_roster_position(th))
		player_height.append(extract_roster_height(th))
		player_weight.append(extract_roster_weight(th))
		player_season.append(extract_roster_season(th))
		player_college.append(extract_roster_college(th))
		player_age.append(extract_roster_age(th))

	player_name[14] = 'Jonas Valanciunas'
	final = [player_name, player_pos, player_height, player_weight, player_season, player_college, player_age]
	return final 

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
	standings = nba_standings() 
	west_standings = standings[3]
	west_wins = standings[4] 
	west_losses = standings[5] 
	west_seed = standings[8]
	team_index = 0 

	roster = rockets_roster_automate()

	for index in range(len(west_standings)):
		if 'rockets' in west_standings[index].lower():
			team_index = index 

	return render_template('rockets.html', wins = west_wins[team_index], losses = west_losses[team_index], seed = west_seed[team_index], 
		player_name = roster[0], player_pos = roster[1], player_height = roster[2], player_weight = roster[3], player_season = roster[4], 
		player_college = roster[5], player_age = roster[6])

#Lakers Page
@app.route('/lakers')
def lakers():
	standings = nba_standings() 
	west_standings = standings[3]
	west_wins = standings[4] 
	west_losses = standings[5] 
	west_seed = standings[8]
	team_index = 0 

	roster = lakers_roster_automate()


	for index in range(len(west_standings)):
		if 'lakers' in west_standings[index].lower():
			team_index = index 

	return render_template('lakers.html', wins = west_wins[team_index], losses = west_losses[team_index], seed = west_seed[team_index], 
		player_name = roster[0], player_pos = roster[1], player_height = roster[2], player_weight = roster[3], player_season = roster[4], 
		player_college = roster[5], player_age = roster[6])

#Nuggets Page
@app.route('/nuggets')
def nuggets():
	return redirect("https://en.wikipedia.org/wiki/Denver_Nuggets")

#Jazz Page
@app.route('/jazz')
def jazz():
	return redirect("https://en.wikipedia.org/wiki/Utah_Jazz")

#Suns Page
@app.route('/suns')
def suns():
	return redirect("https://en.wikipedia.org/wiki/Phoenix_Suns")

#Clippers Page
@app.route('/clippers')
def clippers():
	standings = nba_standings() 
	west_standings = standings[3]
	west_wins = standings[4] 
	west_losses = standings[5] 
	west_seed = standings[8]
	team_index = 0 

	roster = clippers_roster_automate()

	for index in range(len(west_standings)):
		if 'clippers' in west_standings[index].lower():
			team_index = index 

	return render_template('clippers.html', wins = west_wins[team_index], losses = west_losses[team_index], seed = west_seed[team_index], 
		player_name = roster[0], player_pos = roster[1], player_height = roster[2], player_weight = roster[3], player_season = roster[4], 
		player_college = roster[5], player_age = roster[6])

#Mavericks Page
@app.route('/mavericks')
def mavericks():
	return redirect("https://en.wikipedia.org/wiki/Dallas_Mavericks")

#Timberwolves Page
@app.route('/timberwolves')
def timberwolves():
	return redirect("https://en.wikipedia.org/wiki/Minnesota_Timberwolves")

#Grizzlies Page
@app.route('/grizzlies')
def grizzlies():
	standings = nba_standings() 
	west_standings = standings[3]
	west_wins = standings[4] 
	west_losses = standings[5] 
	west_seed = standings[8]
	team_index = 0 

	roster = grizzlies_roster_automate()

	for index in range(len(west_standings)):
		if 'grizzlies' in west_standings[index].lower():
			team_index = index 

	return render_template('grizzlies.html', wins = west_wins[team_index], losses = west_losses[team_index], seed = west_seed[team_index], 
		player_name = roster[0], player_pos = roster[1], player_height = roster[2], player_weight = roster[3], player_season = roster[4], 
		player_college = roster[5], player_age = roster[6])

#Thunder Page
@app.route('/thunder')
def thunder():
	return redirect("https://en.wikipedia.org/wiki/Oklahoma_City_Thunder")

#Blazers Page
@app.route('/blazers')
def blazers():
	return redirect("https://en.wikipedia.org/wiki/Portland_Trailblazers")

#Spurs Page
@app.route('/spurs')
def spurs():
	return redirect("https://en.wikipedia.org/wiki/San_Antonio_Spurs")

#Kings Page
@app.route('/kings')
def kings():
	return redirect("https://en.wikipedia.org/wiki/Sacramento_Kings")

#Pelicans Page
@app.route('/pelicans')
def pelicans():
	return redirect("https://en.wikipedia.org/wiki/New_Orleans_Pelicans")

#Warriors Page
@app.route('/warriors')
def warriors():
	standings = nba_standings() 
	west_standings = standings[3]
	west_wins = standings[4] 
	west_losses = standings[5] 
	west_seed = standings[8]
	team_index = 0 

	roster = warriors_roster_automate()

	for index in range(len(west_standings)):
		if 'warriors' in west_standings[index].lower():
			team_index = index 

	return render_template('warriors.html', wins = west_wins[team_index], losses = west_losses[team_index], seed = west_seed[team_index], 
		player_name = roster[0], player_pos = roster[1], player_height = roster[2], player_weight = roster[3], player_season = roster[4], 
		player_college = roster[5], player_age = roster[6])

#Heat Page
@app.route('/heat')
def heat():
	return redirect("https://en.wikipedia.org/wiki/Miami_Heat")

#Bucks Page
@app.route('/bucks')
def bucks():
	return redirect("https://en.wikipedia.org/wiki/Milwaukee_Bucks")

#Raptors Page
@app.route('/raptors')
def raptors():
	return redirect("https://en.wikipedia.org/wiki/Toronto_Raptors")

#76ers Page
@app.route('/76ers')
def sixers():
	return redirect("https://en.wikipedia.org/wiki/Philadelphia_76ers")

#Pacers Page
@app.route('/pacers')
def pacers():
	return redirect("https://en.wikipedia.org/wiki/Indiana_Pacers")

#Hornets Page
@app.route('/hornets')
def hornets():
	return redirect("https://en.wikipedia.org/wiki/Charlotte_Hornets")

#Cavaliers Page
@app.route('/cavaliers')
def cavaliers():
	return redirect("https://en.wikipedia.org/wiki/Cleveland_Cavaliers")

#Hawks Page
@app.route('/hawks')
def hawks():
	return redirect("https://en.wikipedia.org/wiki/Atlanta_Hawks")

#Bulls Page
@app.route('/bulls')
def bulls():
	return redirect("https://en.wikipedia.org/wiki/Chicago_Bulls")

#Wizards Page
@app.route('/wizards')
def wizards():
	return redirect("https://en.wikipedia.org/wiki/Washington_Wizards")

#Knicks Page
@app.route('/knicks')
def knicks():
	standings = nba_standings() 
	east_standings = standings[0]
	east_wins = standings[1] 
	east_losses = standings[2] 
	east_seed = standings[7]
	team_index = 0 
	roster = knicks_roster_automate()
	for index in range(len(east_standings)):
		if 'knicks' in east_standings[index].lower():
			team_index = index 
	return render_template('knicks.html', wins = east_wins[team_index], losses = east_losses[team_index], seed = east_seed[team_index], 
		player_name = roster[0], player_pos = roster[1], player_height = roster[2], player_weight = roster[3], player_season = roster[4], 
		player_college = roster[5], player_age = roster[6])

#Nets Page
@app.route('/nets')
def nets():
	standings = nba_standings() 
	east_standings = standings[0]
	east_wins = standings[1] 
	east_losses = standings[2] 
	east_seed = standings[7]
	team_index = 0 
	roster = nets_roster_automate()
	for index in range(len(east_standings)):
		if 'nets' in east_standings[index].lower():
			team_index = index 
	return render_template('nets.html', wins = east_wins[team_index], losses = east_losses[team_index], seed = east_seed[team_index], 
		player_name = roster[0], player_pos = roster[1], player_height = roster[2], player_weight = roster[3], player_season = roster[4], 
		player_college = roster[5], player_age = roster[6])

#Pistons Page
@app.route('/pistons')
def pistons():
	standings = nba_standings() 
	east_standings = standings[0]
	east_wins = standings[1] 
	east_losses = standings[2] 
	east_seed = standings[7]
	team_index = 0 
	roster = pistons_roster_automate()
	for index in range(len(east_standings)):
		if 'pistons' in east_standings[index].lower():
			team_index = index 
	return render_template('pistons.html', wins = east_wins[team_index], losses = east_losses[team_index], seed = east_seed[team_index], 
		player_name = roster[0], player_pos = roster[1], player_height = roster[2], player_weight = roster[3], player_season = roster[4], 
		player_college = roster[5], player_age = roster[6])

#Celtics Page
@app.route('/celtics')
def celtics(): 
	standings = nba_standings() 
	east_standings = standings[0]
	east_wins = standings[1] 
	east_losses = standings[2] 
	east_seed = standings[7]
	celtics_index = 0 
	roster = celtics_roster_automate()
	for index in range(len(east_standings)):
		if 'celtics' in east_standings[index].lower():
			celtics_index = index 
	return render_template('celtics.html', wins = east_wins[celtics_index], losses = east_losses[celtics_index], seed = east_seed[celtics_index],
		player_name = roster[0], player_pos = roster[1], player_height = roster[2], player_weight = roster[3], player_season = roster[4], 
		player_college = roster[5], player_age = roster[6])

#Magic Page
@app.route('/magic')
def magic(): 
	standings = nba_standings() 
	east_standings = standings[0]
	east_wins = standings[1] 
	east_losses = standings[2] 
	east_seed = standings[7]
	magic_index = 0 
	roster = magic_roster_automate()
	for index in range(len(east_standings)):
		if 'magic' in east_standings[index].lower():
			magic_index = index 
	return render_template('magic.html', wins = east_wins[magic_index], losses = east_losses[magic_index], seed = east_seed[magic_index], 
		player_name = roster[0], player_pos = roster[1], player_height = roster[2], player_weight = roster[3], player_season = roster[4], 
		player_college = roster[5], player_age = roster[6])


#Patriots Page
@app.route('/patriots')
def patriots():
	return redirect("https://en.wikipedia.org/wiki/New_England_Patriots")

#Bills Page
@app.route('/bills')
def bills():
	return redirect("https://en.wikipedia.org/wiki/Buffalo_Bills")

#Dolphins Page
@app.route('/dolphins')
def dolphins():
	return redirect("https://en.wikipedia.org/wiki/Miami_Dolphins")

#Jets Page 
@app.route('/jets')
def jets():
	return redirect("https://en.wikipedia.org/wiki/New_York_Jets")

#Chiefs Page 
@app.route('/chiefs')
def chiefs():
	return redirect("https://en.wikipedia.org/wiki/Kansas_City_Chiefs")

#Raiders Page 
@app.route('/raiders')
def raiders():
	return redirect("https://en.wikipedia.org/wiki/Oakland_Raiders")

#Chargers Page 
@app.route('/chargers')
def chargers():
	return redirect("https://en.wikipedia.org/wiki/Los_Angeles_Chargers")

#Broncos Page 
@app.route('/broncos')
def broncos():
	return redirect("https://en.wikipedia.org/wiki/Denver_Broncos")

#Ravens Page 
@app.route('/ravens')
def ravens():
	return redirect("https://en.wikipedia.org/wiki/Baltimore_Ravens")

#Steelers Page 
@app.route('/steelers')
def steelers():
	return redirect("https://en.wikipedia.org/wiki/Pittsburgh_Steelers")

#Bengals Page 
@app.route('/bengals')
def bengals():
	return redirect("https://en.wikipedia.org/wiki/Cincinnati_Bengals")

#Browns Page 
@app.route('/browns')
def browns():
	return redirect("https://en.wikipedia.org/wiki/Cleveland_Browns")

#Texans Page 
@app.route('/texans')
def texans():
	return redirect("https://en.wikipedia.org/wiki/Houston_Texans")

#Colts Page 
@app.route('/colts')
def colts():
	return redirect("https://en.wikipedia.org/wiki/Indianapolis_Colts")

#Titans Page 
@app.route('/titans')
def titans():
	return redirect("https://en.wikipedia.org/wiki/Tennessee_Titans")

#Jaguars Page
@app.route('/jaguars')
def jaguars():
	return redirect("https://en.wikipedia.org/wiki/Jacksonville_Jaguars")

#Eagles Page
@app.route('/eagles')
def eagles():
	return redirect("https://en.wikipedia.org/wiki/Philadelphia_Eagles")

#Cowboys Page
@app.route('/cowboys')
def cowboys():
	return redirect("https://en.wikipedia.org/wiki/Dallas_Cowboys")

#Giants Page
@app.route('/giants')
def giants():
	return redirect("https://en.wikipedia.org/wiki/New_York_Giants")

#Redskins Page
@app.route('/redskins')
def redskins():
	return redirect("https://en.wikipedia.org/wiki/Washington_Redskins")

#49ers Page
@app.route('/49ers')
def niners():
	return redirect("https://en.wikipedia.org/wiki/San_Francisco_49ers")

#Seahawks Page
@app.route('/seahawks')
def seahawks():
	return redirect("https://en.wikipedia.org/wiki/Seattle_Seahawks")

#Rams Page
@app.route('/rams')
def rams():
	return redirect("https://en.wikipedia.org/wiki/Los_Angeles_Rams")

#Cardinals Page
@app.route('/cardinals')
def cardinals():
	return redirect("https://en.wikipedia.org/wiki/Arizona_Cardinals")

#Packers Page
@app.route('/packers')
def packers():
	return redirect("https://en.wikipedia.org/wiki/Green_Bay_Packers")

#Vikings Page
@app.route('/vikings')
def vikings():
	return redirect("https://en.wikipedia.org/wiki/Minnesota_Vikings")

#Bears Page
@app.route('/bears')
def bears():
	return redirect("https://en.wikipedia.org/wiki/Chicago_Bears")

#Lions Page
@app.route('/lions')
def lions():
	return redirect("https://en.wikipedia.org/wiki/Detroit_Lions")

#Saints Page
@app.route('/saints')
def saints():
	return redirect("https://en.wikipedia.org/wiki/New_Orleans_Saints")

#Panthers Page
@app.route('/panthers')
def panthers():
	return redirect("https://en.wikipedia.org/wiki/Carolina_Panthers")

#Buccaneers Page
@app.route('/buccaneers')
def buccaneers():
	return redirect("https://en.wikipedia.org/wiki/Tampa_Bay_Buccaneers")

#Falcons Page
@app.route('/falcons')
def falcons():
	return redirect("https://en.wikipedia.org/wiki/Atlanta_Falcons")

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
	nflstandings = nfl_standings()
	afc_east = nflstandings[0:4]
	afc_north = nflstandings[4:8]
	afc_south = nflstandings[8:12]
	afc_west = nflstandings[12:16]
	nfc_east = nflstandings[16:20]
	nfc_north = nflstandings[20:24]
	nfc_south = nflstandings[24:28]
	nfc_west = nflstandings[28:32]
	return render_template('nflteamstandings.html', afceast = afc_east, afcnorth = afc_north, afcsouth = afc_south, afcwest = afc_west, 
		nfceast = nfc_east, nfcnorth = nfc_north, nfcsouth = nfc_south, nfcwest = nfc_west)
	
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