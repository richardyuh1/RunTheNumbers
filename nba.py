from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd 

#Filtered by at least 5 MPG
def category_leader(stats, n, category):
	category_list = []
	for i in range(n): 
		if stats.head(n)[category][i] is None or stats.head(n)[category][i] == '':
			category_list.append(0.0)
		else:
			if stats.head(n)['MP'][i] is not None and stats.head(n)['MP'][i] != '' and float(stats.head(n)['MP'][i]) > 10.0:
				category_list.append(float(stats.head(n)[category][i]))
			else:
				category_list.append(0.0)

	max_pts_index = category_list.index(max(category_list))

	leader = stats.head(n)['Player'][max_pts_index]
	value = max(category_list) 

	return [leader, value]
	#print("Current {} Leader: ".format(category), scoring_leader)
	#print("{}: ".format(category), max(category_list))


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

	stats = pd.DataFrame(player_stats, columns = headers) 

	#Number of players to assess
	n = len(stats)

	category = ['PTS', 'TRB', 'AST', 'BLK', 'MP', '3P%', 'FG%']

	#print(stats.head(n))
	leaders = []

	#Assess PPG
	leaders.append(category_leader(stats, n, category[0]))

	#Assess RPG
	leaders.append(category_leader(stats, n, category[1]))

	#Assess APG
	leaders.append(category_leader(stats, n, category[2]))

	#Assess BPG
	#category_leader(stats, n, category[3])

	#Assess MPG
	#category_leader(stats, n, category[4])

	#Assess 3P% Per Game
	#category_leader(stats, n, category[5])

	#Assess FG% Per Game
	#category_leader(stats, n, category[6])

	return leaders 





