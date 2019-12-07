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
def category_leader(stats, n, category_index, trey_attempt_index, fg_attempt_index, player_index, mp_index, game_index, headers):
	category_list = []
	for i in range(n): 
		if stats[i] is None or len(stats[i]) == 0 or len(stats[i][category_index]) == 0:
			category_list.append(0.0)
		else:
			if stats[i][mp_index] is not None and stats[i][mp_index] != '' and float(stats[i][mp_index]) > 10.0:
				if stats[i][game_index] is not None and stats[i][game_index] != '' and float(stats[i][game_index]) > 5.0:
					if headers[category_index] == '3P%': 
						if float(stats[i][trey_attempt_index]) >= 5.0:
							category_list.append(float(stats[i][category_index]))
						else:
							category_list.append(0.0)
					elif headers[category_index] == 'FG%':
						if float(stats[i][fg_attempt_index]) >= 5.0: 
							category_list.append(float(stats[i][category_index]))
						else:
							category_list.append(0.0)
					else:
						category_list.append(float(stats[i][category_index]))
				else:
					category_list.append(0.0)
			else:
				category_list.append(0.0)

	max_val_index = category_list.index(max(category_list))
	if headers[category_index] == '3P%' or headers[category_index] == 'FG%':
		value = (float(max(category_list))*100)
		value = format(value, '.1f')
	else:
		value = max(category_list) 
	leader = stats[0:n][max_val_index][player_index]

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
	trey_attempt_index = headers.index('3PA')
	fg_percent_index = headers.index('FG%')
	fg_attempt_index = headers.index('FGA')
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
	leaders.append(category_leader(player_stats, n, pts_index, trey_attempt_index, fg_attempt_index, player_index, mp_index, game_index, headers))

	#Assess RPG
	leaders.append(category_leader(player_stats, n, trb_index, trey_attempt_index, fg_attempt_index, player_index, mp_index, game_index, headers))

	#Assess APG
	leaders.append(category_leader(player_stats, n, ast_index, trey_attempt_index, fg_attempt_index, player_index, mp_index, game_index, headers))

	#Assess BPG
	leaders.append(category_leader(player_stats, n, blk_index, trey_attempt_index, fg_attempt_index, player_index, mp_index, game_index, headers))

	#Assess MPG
	#leaders.append(category_leader(player_stats, n, mp_index, trey_attempt_index, fg_attempt_index, player_index, mp_index, headers))

	#Assess 3P% Per Game
	leaders.append(category_leader(player_stats, n, trey_percent_index, trey_attempt_index, fg_attempt_index, player_index, mp_index, game_index, headers))

	#Assess FG% Per Game
	leaders.append(category_leader(player_stats, n, fg_percent_index, trey_attempt_index, fg_attempt_index, player_index, mp_index, game_index, headers))

	return leaders 

####################  NFL Analysis Functions  ##########################
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

def extract_team(th):
	html_line = str(th)
	sub = "teams"
	sub2 = "</a>"
	index = html_line.find(sub)
	index2 = html_line[index:].find(sub2)
	team = html_line[index+20:index+index2]
	return team 

def nfl_run(): 
	#NFL season we will be analyzing
	year = 2020

	#URL page we will be scraping 

	url = "https://www.pro-football-reference.com/leaders/"

	#HTML from given URL 
	html = urlopen(url) 

	soup = BeautifulSoup(html, features='html.parser') 

	th_all = soup.findAll('div', {'class' : 'tabular_row'}, limit = 39)

	team_dict = {'LAC': 'Los Angeles Chargers', 'BAL': 'Baltimore Ravens', 'SEA': 'Seattle Seahawks', 'NOR': 'New Orleans Saints', 'DAL': 'Dallas Cowboys', 
	'NYJ': 'New York Jets', 'TAM': 'Tampa Bay Buccaneers', 'NYG': 'New York Giants', 'DET': 'Detroit Lions', 'CIN': 'Cincinnati Bengals', 'KAN': 'Kansas City Chiefs', 
	'ATL': 'Atlanta Falcons', 'MIN': 'Minnesota Vikings', 'CAR': 'Carolina Panthers', 'NWE': 'New England Patriots', 'TEN': 'Tennessee Titans', 'ARI': 'Arizona Cardinals', 'GNB': 'Green Bay Packers',
	'CLE': 'Cleveland Browns'}

	team_page = {'LAC': '/chargers', 'BAL': '/ravens', 'SEA': '/seahawks', 'NOR': '/saints', 'DAL': '/cowboys', 
	'NYJ': '/jets', 'TAM': '/buccaneers', 'NYG': '/giants', 'DET': '/lions', 'CIN': '/bengals', 'KAN': '/chiefs', 
	'ATL': '/falcons', 'MIN': '/vikings', 'CAR': '/panthers', 'NWE': '/patriots', 'TEN': '/titans', 'ARI': '/cardinals', 'GNB': '/packers', 
	'CLE': 'Cleveland Browns'}

	player_list = [] 
	category_list = [] 
	points_list = [] 
	team_list = []
	team_pages = []

	for th in th_all:
		if len(extract_name(th)) > 30:
			continue
		player_list.append(extract_name(th))
		category_list.append(extract_category(th))
		points_list.append(extract_points(th))
		team_list.append(team_dict[extract_team(th)])
		team_pages.append(team_page[extract_team(th)])

	category_type = ['Passes Completed', 'Passing Yds', 'Passer Rating', 'Passing Yds/Game', 'Pass Completion %', 'Yds/Rushing Att']

	leaders = [] 

	for c in category_type: 
		str_player = player_list[category_list.index(c)]
		str_point = points_list[category_list.index(c)]
		str_team = team_list[category_list.index(c)]
		str_pages = team_pages[category_list.index(c)]
		leaders.append([str_player, str_point, str_team, str_pages])

	return leaders 

################    NBA Team Standings Functions   ####################
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

##################   NFL Team Standings    ##########################
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
		return '1' 
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

def extract_playerjersey(html):
	team_list = ['ATL', 'BOS', 'BRK', 'CHO', 'CHI', 'CLE', 'DAL', 'DET', 'DEN', 'GSW', 'HOU', 'IND', 'LAC', 'LAL', 'MEM', 'MIA', 'MIL', 'MIN', 'NOP', 'NYK', 'OKC', 'ORL', 'POR', 'PHI', 'PHO', 'SAC', 'SAS', 'TOR', 'UTA', 'WAS']
	html = str(html)
	index = html.find("number")
	index2 = html[index:].find("\"")
	jerseyno = html[index+7:index+index2] 
	player_dict = {} 
	index3 = 0
	count = 0 
	while count < 21:
		index3 = html.find("html")
		if index3 == -1:
			break
		index4 = html[index3:].find("</a>")
		player = html[index3 +6:index3+index4]
		if player in team_list:
			html = html[index3+1:]
			continue
		player_dict[player] = jerseyno
		html = html[index3+1:]
		count+=1 
	return player_dict

def nba_jersey_find(): 
	year = 2020

	#URL page we will be scraping 

	url = "https://www.basketball-reference.com/leagues/NBA_{}_numbers.html".format(year)

	#HTML from given URL 
	html = urlopen(url) 

	soup = BeautifulSoup(html, features='html.parser') 

	#use findAll() to get column headers
	html_raw = soup.findAll('div', {'class': 'data_grid_box'})

	jersey_list = [] 

	for html in html_raw:
		jersey_list.append(extract_playerjersey(html))

	return jersey_list 

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

	#Jersey No
	jersey_list = nba_jersey_find()

	final = [player_name, player_pos, player_height, player_weight, player_season, player_college, player_age, jersey_list]
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

	for i in range(len(player_name)):
		if 'Ne' in player_name[i] :
			player_name[i] = 'Nene'

	#Jersey No
	jersey_list = nba_jersey_find()

	final = [player_name, player_pos, player_height, player_weight, player_season, player_college, player_age, jersey_list]
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

	#Jersey No
	jersey_list = nba_jersey_find()

	final = [player_name, player_pos, player_height, player_weight, player_season, player_college, player_age, jersey_list]
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

	#Jersey No
	jersey_list = nba_jersey_find()

	final = [player_name, player_pos, player_height, player_weight, player_season, player_college, player_age, jersey_list]
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

	#Jersey No
	jersey_list = nba_jersey_find()

	final = [player_name, player_pos, player_height, player_weight, player_season, player_college, player_age, jersey_list]
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

	#Jersey No
	jersey_list = nba_jersey_find()

	final = [player_name, player_pos, player_height, player_weight, player_season, player_college, player_age, jersey_list]
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

	for th in th_all:
		player_name.append(extract_roster_name(th))
		player_pos.append(extract_roster_position(th))
		player_height.append(extract_roster_height(th))
		player_weight.append(extract_roster_weight(th))
		player_season.append(extract_roster_season(th))
		player_college.append(extract_roster_college(th))
		player_age.append(extract_roster_age(th))

	#Jersey No
	jersey_list = nba_jersey_find()

	final = [player_name, player_pos, player_height, player_weight, player_season, player_college, player_age, jersey_list]
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

	#Jersey No
	jersey_list = nba_jersey_find()

	final = [player_name, player_pos, player_height, player_weight, player_season, player_college, player_age, jersey_list]
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

	#Jersey No
	jersey_list = nba_jersey_find()

	final = [player_name, player_pos, player_height, player_weight, player_season, player_college, player_age, jersey_list]
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

	#Jersey No
	jersey_list = nba_jersey_find()

	final = [player_name, player_pos, player_height, player_weight, player_season, player_college, player_age, jersey_list]
	return final 

def hawks_roster_automate():
	year = 2020

	#URL page we will be scraping 

	url = "https://www.basketball-reference.com/teams/ATL/{}.html".format(year)

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

	#Jersey No
	jersey_list = nba_jersey_find()

	final = [player_name, player_pos, player_height, player_weight, player_season, player_college, player_age, jersey_list]
	return final 

def hornets_roster_automate():
	year = 2020

	#URL page we will be scraping 

	url = "https://www.basketball-reference.com/teams/CHO/{}.html".format(year)

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

	#Jersey No
	jersey_list = nba_jersey_find()

	final = [player_name, player_pos, player_height, player_weight, player_season, player_college, player_age, jersey_list]
	return final 

def bulls_roster_automate():
	year = 2020

	#URL page we will be scraping 

	url = "https://www.basketball-reference.com/teams/CHI/{}.html".format(year)

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

	#Jersey No
	jersey_list = nba_jersey_find()

	final = [player_name, player_pos, player_height, player_weight, player_season, player_college, player_age, jersey_list]
	return final 

def cavaliers_roster_automate():
	year = 2020

	#URL page we will be scraping 

	url = "https://www.basketball-reference.com/teams/CLE/{}.html".format(year)

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

	#Jersey No
	jersey_list = nba_jersey_find()

	final = [player_name, player_pos, player_height, player_weight, player_season, player_college, player_age, jersey_list]
	return final 

def mavericks_roster_automate():
	year = 2020

	#URL page we will be scraping 

	url = "https://www.basketball-reference.com/teams/DAL/{}.html".format(year)

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
	
	#Jersey No
	jersey_list = nba_jersey_find()

	final = [player_name, player_pos, player_height, player_weight, player_season, player_college, player_age, jersey_list]
	return final 

def nuggets_roster_automate():
	year = 2020

	#URL page we will be scraping 

	url = "https://www.basketball-reference.com/teams/DEN/{}.html".format(year)

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
	
	#Jersey No
	jersey_list = nba_jersey_find()

	final = [player_name, player_pos, player_height, player_weight, player_season, player_college, player_age, jersey_list]
	return final 

def pacers_roster_automate():
	year = 2020

	#URL page we will be scraping 

	url = "https://www.basketball-reference.com/teams/IND/{}.html".format(year)

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

	
	#Jersey No
	jersey_list = nba_jersey_find()

	final = [player_name, player_pos, player_height, player_weight, player_season, player_college, player_age, jersey_list]
	return final 

def heat_roster_automate():
	year = 2020

	#URL page we will be scraping 

	url = "https://www.basketball-reference.com/teams/MIA/{}.html".format(year)

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

	#Jersey No
	jersey_list = nba_jersey_find()

	final = [player_name, player_pos, player_height, player_weight, player_season, player_college, player_age, jersey_list]
	return final 

def bucks_roster_automate():
	year = 2020

	#URL page we will be scraping 

	url = "https://www.basketball-reference.com/teams/MIL/{}.html".format(year)

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

	#Jersey No
	jersey_list = nba_jersey_find()

	final = [player_name, player_pos, player_height, player_weight, player_season, player_college, player_age, jersey_list]
	return final 

def timberwolves_roster_automate():
	year = 2020

	#URL page we will be scraping 

	url = "https://www.basketball-reference.com/teams/MIN/{}.html".format(year)

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


	#Jersey No
	jersey_list = nba_jersey_find()

	final = [player_name, player_pos, player_height, player_weight, player_season, player_college, player_age, jersey_list]
	return final 

def pelicans_roster_automate():
	year = 2020

	#URL page we will be scraping 

	url = "https://www.basketball-reference.com/teams/NOP/{}.html".format(year)

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

	#Jersey No
	jersey_list = nba_jersey_find()

	final = [player_name, player_pos, player_height, player_weight, player_season, player_college, player_age, jersey_list]
	return final 

def thunder_roster_automate():
	year = 2020

	#URL page we will be scraping 

	url = "https://www.basketball-reference.com/teams/OKC/{}.html".format(year)

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

	#Jersey No
	jersey_list = nba_jersey_find()

	final = [player_name, player_pos, player_height, player_weight, player_season, player_college, player_age, jersey_list]
	return final 

def blazers_roster_automate():
	year = 2020

	#URL page we will be scraping 

	url = "https://www.basketball-reference.com/teams/POR/{}.html".format(year)

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

	for i in range(len(player_name)):
		if 'Skal' in player_name[i]:
			player_name[i] = 'Skal Labissiere'
		if 'Jusuf' in player_name[i]:
			player_name[i] = 'Jusuf Nurkic'

	#Jersey No
	jersey_list = nba_jersey_find()

	final = [player_name, player_pos, player_height, player_weight, player_season, player_college, player_age, jersey_list]
	return final 

def sixers_roster_automate():
	year = 2020

	#URL page we will be scraping 

	url = "https://www.basketball-reference.com/teams/PHI/{}.html".format(year)

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

	#Jersey No
	jersey_list = nba_jersey_find()

	final = [player_name, player_pos, player_height, player_weight, player_season, player_college, player_age, jersey_list]
	return final 

def suns_roster_automate():
	year = 2020

	#URL page we will be scraping 

	url = "https://www.basketball-reference.com/teams/PHO/{}.html".format(year)

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
	
	#for i in range(len(player_name)):
		#if 'Dario' in player_name[i]:
			#player_name[i] = 'Dario Saric'
	
	#Jersey No
	jersey_list = nba_jersey_find()

	final = [player_name, player_pos, player_height, player_weight, player_season, player_college, player_age, jersey_list]
	
	return final 

def kings_roster_automate():
	year = 2020

	#URL page we will be scraping 

	url = "https://www.basketball-reference.com/teams/SAC/{}.html".format(year)

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

	#Jersey No
	jersey_list = nba_jersey_find()

	final = [player_name, player_pos, player_height, player_weight, player_season, player_college, player_age, jersey_list]
	return final 

def spurs_roster_automate():
	year = 2020

	#URL page we will be scraping 

	url = "https://www.basketball-reference.com/teams/SAS/{}.html".format(year)

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

	#Jersey No
	jersey_list = nba_jersey_find()

	final = [player_name, player_pos, player_height, player_weight, player_season, player_college, player_age, jersey_list]
	return final 

def raptors_roster_automate():
	year = 2020

	#URL page we will be scraping 

	url = "https://www.basketball-reference.com/teams/TOR/{}.html".format(year)

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
	
	#Jersey No
	jersey_list = nba_jersey_find()

	final = [player_name, player_pos, player_height, player_weight, player_season, player_college, player_age, jersey_list]
	return final 

def jazz_roster_automate():
	year = 2020

	#URL page we will be scraping 

	url = "https://www.basketball-reference.com/teams/UTA/{}.html".format(year)

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

	#Jersey No
	jersey_list = nba_jersey_find()

	final = [player_name, player_pos, player_height, player_weight, player_season, player_college, player_age, jersey_list]
	return final 

def wizards_roster_automate():
	year = 2020

	#URL page we will be scraping 

	url = "https://www.basketball-reference.com/teams/WAS/{}.html".format(year)

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

	#Jersey No
	jersey_list = nba_jersey_find()

	final = [player_name, player_pos, player_height, player_weight, player_season, player_college, player_age, jersey_list]
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

	jerseylist = roster[7]
	rockets_jersey = [] 
	for name in roster[0]:
		for jersey in jerseylist:
			if name in jersey.keys():
				rockets_jersey.append([jersey[name], name])

	return render_template('rockets.html', wins = west_wins[team_index], losses = west_losses[team_index], seed = west_seed[team_index], 
		player_name = roster[0], player_pos = roster[1], player_height = roster[2], player_weight = roster[3], player_season = roster[4], 
		player_college = roster[5], player_age = roster[6], rocketsjersey = rockets_jersey)

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

	jerseylist = roster[7]
	lakers_jersey = [] 
	for name in roster[0]:
		for jersey in jerseylist:
			if name in jersey.keys():
				lakers_jersey.append([jersey[name], name])

	return render_template('lakers.html', wins = west_wins[team_index], losses = west_losses[team_index], seed = west_seed[team_index], 
		player_name = roster[0], player_pos = roster[1], player_height = roster[2], player_weight = roster[3], player_season = roster[4], 
		player_college = roster[5], player_age = roster[6], lakersjersey = lakers_jersey)

#Nuggets Page
@app.route('/nuggets')
def nuggets():
	standings = nba_standings() 
	west_standings = standings[3]
	west_wins = standings[4] 
	west_losses = standings[5] 
	west_seed = standings[8]
	team_index = 0 

	roster = nuggets_roster_automate()


	for index in range(len(west_standings)):
		if 'nuggets' in west_standings[index].lower():
			team_index = index 

	jerseylist = roster[7]
	nuggets_jersey = [] 
	for name in roster[0]:
		for jersey in jerseylist:
			if name in jersey.keys():
				nuggets_jersey.append([jersey[name], name])

	return render_template('nuggets.html', wins = west_wins[team_index], losses = west_losses[team_index], seed = west_seed[team_index], 
		player_name = roster[0], player_pos = roster[1], player_height = roster[2], player_weight = roster[3], player_season = roster[4], 
		player_college = roster[5], player_age = roster[6], nuggetsjersey = nuggets_jersey)

#Jazz Page
@app.route('/jazz')
def jazz():
	standings = nba_standings() 
	west_standings = standings[3]
	west_wins = standings[4] 
	west_losses = standings[5] 
	west_seed = standings[8]
	team_index = 0 

	roster = jazz_roster_automate()

	for index in range(len(west_standings)):
		if 'jazz' in west_standings[index].lower():
			team_index = index 

	jerseylist = roster[7]
	jazz_jersey = [] 
	for name in roster[0]:
		for jersey in jerseylist:
			if name in jersey.keys():
				jazz_jersey.append([jersey[name], name])

	return render_template('jazz.html', wins = west_wins[team_index], losses = west_losses[team_index], seed = west_seed[team_index], 
		player_name = roster[0], player_pos = roster[1], player_height = roster[2], player_weight = roster[3], player_season = roster[4], 
		player_college = roster[5], player_age = roster[6], jazzjersey = jazz_jersey)

#Suns Page
@app.route('/suns')
def suns():
	standings = nba_standings() 
	west_standings = standings[3]
	west_wins = standings[4] 
	west_losses = standings[5] 
	west_seed = standings[8]
	team_index = 0 

	roster = suns_roster_automate()

	for index in range(len(west_standings)):
		if 'suns' in west_standings[index].lower():
			team_index = index 

	jerseylist = roster[7]
	suns_jersey = [] 
	for name in roster[0]:
		for jersey in jerseylist:
			if name in jersey.keys():
				suns_jersey.append([jersey[name], name])

	return render_template('suns.html', wins = west_wins[team_index], losses = west_losses[team_index], seed = west_seed[team_index], 
		player_name = roster[0], player_pos = roster[1], player_height = roster[2], player_weight = roster[3], player_season = roster[4], 
		player_college = roster[5], player_age = roster[6], sunsjersey = suns_jersey)

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

	jerseylist = roster[7]
	clippers_jersey = [] 
	for name in roster[0]:
		for jersey in jerseylist:
			if name in jersey.keys():
				clippers_jersey.append([jersey[name], name])

	return render_template('clippers.html', wins = west_wins[team_index], losses = west_losses[team_index], seed = west_seed[team_index], 
		player_name = roster[0], player_pos = roster[1], player_height = roster[2], player_weight = roster[3], player_season = roster[4], 
		player_college = roster[5], player_age = roster[6], clippersjersey = clippers_jersey)

#Mavericks Page
@app.route('/mavericks')
def mavericks():
	standings = nba_standings() 
	west_standings = standings[3]
	west_wins = standings[4] 
	west_losses = standings[5] 
	west_seed = standings[8]
	team_index = 0 

	roster = mavericks_roster_automate()


	for index in range(len(west_standings)):
		if 'mavericks' in west_standings[index].lower():
			team_index = index 

	jerseylist = roster[7]
	mavericks_jersey = [] 
	for name in roster[0]:
		for jersey in jerseylist:
			if name in jersey.keys():
				mavericks_jersey.append([jersey[name], name])

	return render_template('mavericks.html', wins = west_wins[team_index], losses = west_losses[team_index], seed = west_seed[team_index], 
		player_name = roster[0], player_pos = roster[1], player_height = roster[2], player_weight = roster[3], player_season = roster[4], 
		player_college = roster[5], player_age = roster[6], mavericksjersey = mavericks_jersey)

#Timberwolves Page
@app.route('/timberwolves')
def timberwolves():
	standings = nba_standings() 
	west_standings = standings[3]
	west_wins = standings[4] 
	west_losses = standings[5] 
	west_seed = standings[8]
	team_index = 0 

	roster = timberwolves_roster_automate()

	for index in range(len(west_standings)):
		if 'timberwolves' in west_standings[index].lower():
			team_index = index 

	jerseylist = roster[7]
	wolves_jersey = [] 
	for name in roster[0]:
		for jersey in jerseylist:
			if name in jersey.keys():
				wolves_jersey.append([jersey[name], name])

	return render_template('timberwolves.html', wins = west_wins[team_index], losses = west_losses[team_index], seed = west_seed[team_index], 
		player_name = roster[0], player_pos = roster[1], player_height = roster[2], player_weight = roster[3], player_season = roster[4], 
		player_college = roster[5], player_age = roster[6], wolvesjersey = wolves_jersey)

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

	jerseylist = roster[7]
	grizzlies_jersey = [] 
	for name in roster[0]:
		for jersey in jerseylist:
			if name in jersey.keys():
				grizzlies_jersey.append([jersey[name], name])

	return render_template('grizzlies.html', wins = west_wins[team_index], losses = west_losses[team_index], seed = west_seed[team_index], 
		player_name = roster[0], player_pos = roster[1], player_height = roster[2], player_weight = roster[3], player_season = roster[4], 
		player_college = roster[5], player_age = roster[6], grizzliesjersey = grizzlies_jersey)

#Thunder Page
@app.route('/thunder')
def thunder():
	standings = nba_standings() 
	west_standings = standings[3]
	west_wins = standings[4] 
	west_losses = standings[5] 
	west_seed = standings[8]
	team_index = 0 

	roster = thunder_roster_automate()

	for index in range(len(west_standings)):
		if 'thunder' in west_standings[index].lower():
			team_index = index 

	jerseylist = roster[7]
	thunder_jersey = [] 
	for name in roster[0]:
		for jersey in jerseylist:
			if name in jersey.keys():
				thunder_jersey.append([jersey[name], name])

	return render_template('thunder.html', wins = west_wins[team_index], losses = west_losses[team_index], seed = west_seed[team_index], 
		player_name = roster[0], player_pos = roster[1], player_height = roster[2], player_weight = roster[3], player_season = roster[4], 
		player_college = roster[5], player_age = roster[6], thunderjersey = thunder_jersey)

#Blazers Page
@app.route('/trailblazers')
def blazers():
	standings = nba_standings() 
	west_standings = standings[3]
	west_wins = standings[4] 
	west_losses = standings[5] 
	west_seed = standings[8]
	team_index = 0 

	roster = blazers_roster_automate()


	for index in range(len(west_standings)):
		if 'blazers' in west_standings[index].lower():
			team_index = index 

	jerseylist = roster[7]
	blazers_jersey = [] 
	for name in roster[0]:
		for jersey in jerseylist:
			if name in jersey.keys():
				blazers_jersey.append([jersey[name], name])

	return render_template('trailblazers.html', wins = west_wins[team_index], losses = west_losses[team_index], seed = west_seed[team_index], 
		player_name = roster[0], player_pos = roster[1], player_height = roster[2], player_weight = roster[3], player_season = roster[4], 
		player_college = roster[5], player_age = roster[6], blazersjersey = blazers_jersey)

#Spurs Page
@app.route('/spurs')
def spurs():
	standings = nba_standings() 
	west_standings = standings[3]
	west_wins = standings[4] 
	west_losses = standings[5] 
	west_seed = standings[8]
	team_index = 0 

	roster = spurs_roster_automate()


	for index in range(len(west_standings)):
		if 'spurs' in west_standings[index].lower():
			team_index = index 

	jerseylist = roster[7]
	spurs_jersey = [] 
	for name in roster[0]:
		for jersey in jerseylist:
			if name in jersey.keys():
				spurs_jersey.append([jersey[name], name])

	return render_template('spurs.html', wins = west_wins[team_index], losses = west_losses[team_index], seed = west_seed[team_index], 
		player_name = roster[0], player_pos = roster[1], player_height = roster[2], player_weight = roster[3], player_season = roster[4], 
		player_college = roster[5], player_age = roster[6], spursjersey = spurs_jersey)

#Kings Page
@app.route('/kings')
def kings():
	standings = nba_standings() 
	west_standings = standings[3]
	west_wins = standings[4] 
	west_losses = standings[5] 
	west_seed = standings[8]
	team_index = 0 

	roster = kings_roster_automate()


	for index in range(len(west_standings)):
		if 'kings' in west_standings[index].lower():
			team_index = index 

	jerseylist = roster[7]
	kings_jersey = [] 
	for name in roster[0]:
		for jersey in jerseylist:
			if name in jersey.keys():
				kings_jersey.append([jersey[name], name])

	return render_template('kings.html', wins = west_wins[team_index], losses = west_losses[team_index], seed = west_seed[team_index], 
		player_name = roster[0], player_pos = roster[1], player_height = roster[2], player_weight = roster[3], player_season = roster[4], 
		player_college = roster[5], player_age = roster[6], kingsjersey = kings_jersey)

#Pelicans Page
@app.route('/pelicans')
def pelicans():
	standings = nba_standings() 
	west_standings = standings[3]
	west_wins = standings[4] 
	west_losses = standings[5] 
	west_seed = standings[8]
	team_index = 0 

	roster = pelicans_roster_automate()


	for index in range(len(west_standings)):
		if 'pelicans' in west_standings[index].lower():
			team_index = index 

	jerseylist = roster[7]
	pelicans_jersey = [] 
	for name in roster[0]:
		for jersey in jerseylist:
			if name in jersey.keys():
				pelicans_jersey.append([jersey[name], name])

	return render_template('pelicans.html', wins = west_wins[team_index], losses = west_losses[team_index], seed = west_seed[team_index], 
		player_name = roster[0], player_pos = roster[1], player_height = roster[2], player_weight = roster[3], player_season = roster[4], 
		player_college = roster[5], player_age = roster[6], pelicansjersey = pelicans_jersey)

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

	jerseylist = roster[7]
	warriors_jersey = [] 
	for name in roster[0]:
		for jersey in jerseylist:
			if name in jersey.keys():
				warriors_jersey.append([jersey[name], name])

	return render_template('warriors.html', wins = west_wins[team_index], losses = west_losses[team_index], seed = west_seed[team_index], 
		player_name = roster[0], player_pos = roster[1], player_height = roster[2], player_weight = roster[3], player_season = roster[4], 
		player_college = roster[5], player_age = roster[6], warriorsjersey = warriors_jersey)

#Heat Page
@app.route('/heat')
def heat():
	standings = nba_standings() 
	east_standings = standings[0]
	east_wins = standings[1] 
	east_losses = standings[2] 
	east_seed = standings[7]
	team_index = 0 
	roster = heat_roster_automate()
	for index in range(len(east_standings)):
		if 'heat' in east_standings[index].lower():
			team_index = index 

	jerseylist = roster[7]
	heat_jersey = [] 
	for name in roster[0]:
		for jersey in jerseylist:
			if name in jersey.keys():
				heat_jersey.append([jersey[name], name])

	return render_template('heat.html', wins = east_wins[team_index], losses = east_losses[team_index], seed = east_seed[team_index], 
		player_name = roster[0], player_pos = roster[1], player_height = roster[2], player_weight = roster[3], player_season = roster[4], 
		player_college = roster[5], player_age = roster[6], heatjersey = heat_jersey)

#Bucks Page
@app.route('/bucks')
def bucks():
	standings = nba_standings() 
	east_standings = standings[0]
	east_wins = standings[1] 
	east_losses = standings[2] 
	east_seed = standings[7]
	team_index = 0 
	roster = bucks_roster_automate()
	for index in range(len(east_standings)):
		if 'bucks' in east_standings[index].lower():
			team_index = index 

	jerseylist = roster[7]
	bucks_jersey = [] 
	for name in roster[0]:
		for jersey in jerseylist:
			if name in jersey.keys():
				bucks_jersey.append([jersey[name], name])

	return render_template('bucks.html', wins = east_wins[team_index], losses = east_losses[team_index], seed = east_seed[team_index], 
		player_name = roster[0], player_pos = roster[1], player_height = roster[2], player_weight = roster[3], player_season = roster[4], 
		player_college = roster[5], player_age = roster[6], bucksjersey = bucks_jersey)

#Raptors Page
@app.route('/raptors')
def raptors():
	standings = nba_standings() 
	east_standings = standings[0]
	east_wins = standings[1] 
	east_losses = standings[2] 
	east_seed = standings[7]
	team_index = 0 
	roster = raptors_roster_automate()
	for index in range(len(east_standings)):
		if 'raptors' in east_standings[index].lower():
			team_index = index 

	jerseylist = roster[7]
	raptors_jersey = [] 
	for name in roster[0]:
		for jersey in jerseylist:
			if name in jersey.keys():
				raptors_jersey.append([jersey[name], name])

	return render_template('raptors.html', wins = east_wins[team_index], losses = east_losses[team_index], seed = east_seed[team_index], 
		player_name = roster[0], player_pos = roster[1], player_height = roster[2], player_weight = roster[3], player_season = roster[4], 
		player_college = roster[5], player_age = roster[6], raptorsjersey = raptors_jersey)

#76ers Page
@app.route('/76ers')
def sixers():
	standings = nba_standings() 
	east_standings = standings[0]
	east_wins = standings[1] 
	east_losses = standings[2] 
	east_seed = standings[7]
	team_index = 0 
	roster = sixers_roster_automate()
	for index in range(len(east_standings)):
		if '76ers' in east_standings[index].lower():
			team_index = index 
	jerseylist = roster[7]
	sixers_jersey = [] 
	for name in roster[0]:
		for jersey in jerseylist:
			if name in jersey.keys():
				sixers_jersey.append([jersey[name], name])

	return render_template('76ers.html', wins = east_wins[team_index], losses = east_losses[team_index], seed = east_seed[team_index], 
		player_name = roster[0], player_pos = roster[1], player_height = roster[2], player_weight = roster[3], player_season = roster[4], 
		player_college = roster[5], player_age = roster[6], sixersjersey = sixers_jersey)

#Pacers Page
@app.route('/pacers')
def pacers():
	standings = nba_standings() 
	east_standings = standings[0]
	east_wins = standings[1] 
	east_losses = standings[2] 
	east_seed = standings[7]
	team_index = 0 
	roster = pacers_roster_automate()
	for index in range(len(east_standings)):
		if 'pacers' in east_standings[index].lower():
			team_index = index 

	jerseylist = roster[7]
	pacers_jersey = [] 
	for name in roster[0]:
		for jersey in jerseylist:
			if name in jersey.keys():
				pacers_jersey.append([jersey[name], name])

	return render_template('pacers.html', wins = east_wins[team_index], losses = east_losses[team_index], seed = east_seed[team_index], 
		player_name = roster[0], player_pos = roster[1], player_height = roster[2], player_weight = roster[3], player_season = roster[4], 
		player_college = roster[5], player_age = roster[6], pacersjersey = pacers_jersey)

#Hornets Page
@app.route('/hornets')
def hornets():
	standings = nba_standings() 
	east_standings = standings[0]
	east_wins = standings[1] 
	east_losses = standings[2] 
	east_seed = standings[7]
	team_index = 0 
	roster = hornets_roster_automate()
	for index in range(len(east_standings)):
		if 'hornets' in east_standings[index].lower():
			team_index = index 

	jerseylist = roster[7]
	hornets_jersey = [] 
	for name in roster[0]:
		for jersey in jerseylist:
			if name in jersey.keys():
				hornets_jersey.append([jersey[name], name])

	return render_template('hornets.html', wins = east_wins[team_index], losses = east_losses[team_index], seed = east_seed[team_index], 
		player_name = roster[0], player_pos = roster[1], player_height = roster[2], player_weight = roster[3], player_season = roster[4], 
		player_college = roster[5], player_age = roster[6], hornetsjersey = hornets_jersey)

#Cavaliers Page
@app.route('/cavaliers')
def cavaliers():
	standings = nba_standings() 
	east_standings = standings[0]
	east_wins = standings[1] 
	east_losses = standings[2] 
	east_seed = standings[7]
	team_index = 0 
	roster = cavaliers_roster_automate()
	for index in range(len(east_standings)):
		if 'cavaliers' in east_standings[index].lower():
			team_index = index 

	jerseylist = roster[7]
	cavaliers_jersey = [] 
	for name in roster[0]:
		for jersey in jerseylist:
			if name in jersey.keys():
				cavaliers_jersey.append([jersey[name], name])

	return render_template('cavaliers.html', wins = east_wins[team_index], losses = east_losses[team_index], seed = east_seed[team_index], 
		player_name = roster[0], player_pos = roster[1], player_height = roster[2], player_weight = roster[3], player_season = roster[4], 
		player_college = roster[5], player_age = roster[6], cavaliersjersey = cavaliers_jersey)

#Hawks Page
@app.route('/hawks')
def hawks():
	standings = nba_standings() 
	east_standings = standings[0]
	east_wins = standings[1] 
	east_losses = standings[2] 
	east_seed = standings[7]
	team_index = 0 
	roster = hawks_roster_automate()
	for index in range(len(east_standings)):
		if 'hawks' in east_standings[index].lower():
			team_index = index 

	jerseylist = roster[7]
	hawks_jersey = [] 
	for name in roster[0]:
		for jersey in jerseylist:
			if name in jersey.keys():
				hawks_jersey.append([jersey[name], name])

	return render_template('hawks.html', wins = east_wins[team_index], losses = east_losses[team_index], seed = east_seed[team_index], 
		player_name = roster[0], player_pos = roster[1], player_height = roster[2], player_weight = roster[3], player_season = roster[4], 
		player_college = roster[5], player_age = roster[6], hawksjersey = hawks_jersey)

#Bulls Page
@app.route('/bulls')
def bulls():
	standings = nba_standings() 
	east_standings = standings[0]
	east_wins = standings[1] 
	east_losses = standings[2] 
	east_seed = standings[7]
	team_index = 0 
	roster = bulls_roster_automate()
	for index in range(len(east_standings)):
		if 'bulls' in east_standings[index].lower():
			team_index = index 

	jerseylist = roster[7]
	bulls_jersey = [] 
	for name in roster[0]:
		for jersey in jerseylist:
			if name in jersey.keys():
				bulls_jersey.append([jersey[name], name])

	return render_template('bulls.html', wins = east_wins[team_index], losses = east_losses[team_index], seed = east_seed[team_index], 
		player_name = roster[0], player_pos = roster[1], player_height = roster[2], player_weight = roster[3], player_season = roster[4], 
		player_college = roster[5], player_age = roster[6], bullsjersey = bulls_jersey)

#Wizards Page
@app.route('/wizards')
def wizards():
	standings = nba_standings() 
	east_standings = standings[0]
	east_wins = standings[1] 
	east_losses = standings[2] 
	east_seed = standings[7]
	team_index = 0 
	roster = wizards_roster_automate()
	for index in range(len(east_standings)):
		if 'wizards' in east_standings[index].lower():
			team_index = index 

	jerseylist = roster[7]
	wizards_jersey = [] 
	for name in roster[0]:
		for jersey in jerseylist:
			if name in jersey.keys():
				wizards_jersey.append([jersey[name], name])

	return render_template('wizards.html', wins = east_wins[team_index], losses = east_losses[team_index], seed = east_seed[team_index], 
		player_name = roster[0], player_pos = roster[1], player_height = roster[2], player_weight = roster[3], player_season = roster[4], 
		player_college = roster[5], player_age = roster[6], wizardsjersey = wizards_jersey)

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

	jerseylist = roster[7]
	knicks_jersey = [] 
	for name in roster[0]:
		for jersey in jerseylist:
			if name in jersey.keys():
				knicks_jersey.append([jersey[name], name])

	return render_template('knicks.html', wins = east_wins[team_index], losses = east_losses[team_index], seed = east_seed[team_index], 
		player_name = roster[0], player_pos = roster[1], player_height = roster[2], player_weight = roster[3], player_season = roster[4], 
		player_college = roster[5], player_age = roster[6], knicksjersey = knicks_jersey)

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

	jerseylist = roster[7]
	nets_jersey = [] 
	for name in roster[0]:
		for jersey in jerseylist:
			if name in jersey.keys():
				nets_jersey.append([jersey[name], name])

	return render_template('nets.html', wins = east_wins[team_index], losses = east_losses[team_index], seed = east_seed[team_index], 
		player_name = roster[0], player_pos = roster[1], player_height = roster[2], player_weight = roster[3], player_season = roster[4], 
		player_college = roster[5], player_age = roster[6], netsjersey = nets_jersey)

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

	jerseylist = roster[7]
	pistons_jersey = [] 
	for name in roster[0]:
		for jersey in jerseylist:
			if name in jersey.keys():
				pistons_jersey.append([jersey[name], name])

	return render_template('pistons.html', wins = east_wins[team_index], losses = east_losses[team_index], seed = east_seed[team_index], 
		player_name = roster[0], player_pos = roster[1], player_height = roster[2], player_weight = roster[3], player_season = roster[4], 
		player_college = roster[5], player_age = roster[6], pistonsjersey = pistons_jersey)

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

	jerseylist = roster[7]
	celtics_jersey = [] 
	for name in roster[0]:
		for jersey in jerseylist:
			if name in jersey.keys():
				celtics_jersey.append([jersey[name], name])

	return render_template('celtics.html', wins = east_wins[celtics_index], losses = east_losses[celtics_index], seed = east_seed[celtics_index], 
		player_name = roster[0], player_pos = roster[1], player_height = roster[2], player_weight = roster[3], player_season = roster[4], 
		player_college = roster[5], player_age = roster[6], celticsjersey = celtics_jersey)

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

	jerseylist = roster[7]
	magic_jersey = [] 
	for name in roster[0]:
		for jersey in jerseylist:
			if name in jersey.keys():
				magic_jersey.append([jersey[name], name])

	return render_template('magic.html', wins = east_wins[magic_index], losses = east_losses[magic_index], seed = east_seed[magic_index], 
		player_name = roster[0], player_pos = roster[1], player_height = roster[2], player_weight = roster[3], player_season = roster[4], 
		player_college = roster[5], player_age = roster[6], magicjersey = magic_jersey)


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
		val3 = leader_list[2][1], val4 = leader_list[3][1], val5 = leader_list[4][1], val6 = leader_list[5][1], team1 = leader_list[0][2], 
		team2 = leader_list[1][2], team3 = leader_list[2][2], team4 = leader_list[3][2], team5 = leader_list[4][2], team6 = leader_list[5][2], 
		page1 = leader_list[0][3], page2 = leader_list[1][3], page3 = leader_list[2][3], page4 = leader_list[3][3], page5 = leader_list[4][3], 
		page6 = leader_list[5][3])

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