from bs4 import BeautifulSoup as BS
from requests import get
import re
import pandas as pd

import unicodedata

from page_scraper import compiled_info
from sentiment_analysis import analyze_comments
import time

start_time=time.time()

def strip_accents(s):
   return ''.join(c for c in unicodedata.normalize('NFD', s)
                  if unicodedata.category(c) != 'Mn')

def link_scraper(url):
	r=get(url)
	soup=BS(r.text,"html.parser")
	
	try:
		manga=soup.find_all("div",{"class":"search-story-item"})[0]
	except Exception as e:
		print(e)
		return None
		
	try:	
		manga_link=manga.find_all("div",{"class":"item-right"})[0].h3.a['href']
	except Exception as e:
		print("manga link unavailable")
		print(e)
		manga_link=None

	return manga_link


url="https://www.animenewsnetwork.com/encyclopedia/ratings-manga.php?top50=popular&n=500"
r=get(url)
soup=BS(r.text,"html.parser")

mangas=soup.find_all("tr",{"bgcolor":"#EEEEEE"})

manga=mangas[31]

failed_attempts=[]

SA=[]
ANN=[]
MR=[]
total_views=[]
manga_index=[]
total_comments=[]

for manga in mangas:

	o_manga_name=manga.find_all("td",{"class":"t"})[0].text
	manga_name=o_manga_name
	manga_rating=manga.find_all("td",{"class":"r"})[0].text
	print("SCRAPING :" + str(manga_name))
	print("-----------------------------------------------")
	print("\n\n")
	
	manga_name=re.sub("[\(\[].*?[\)\]]",'', str(manga_name))
	manga_name=re.sub(r"\W+|_", " ", manga_name)
	manga_name=manga_name.replace(" ","_")
	manga_name=strip_accents(str(manga_name))
	
	redirect_url="https://m.manganelo.com/search/story/" + str(manga_name)
	new_url=link_scraper(redirect_url)
	if new_url==None:
		failed_attempts.append(manga_name)
		print(str(manga_name) + " not available\n")
		print("-----------------------------------------------")
		continue
		
	try:
		all_data=compiled_info(new_url)
	except Exception as e:
		failed_attempts.append(manga_name)
		print(str(manga_name) + " not available\n")
		print("-----------------------------------------------")
		print(e)
		continue
		
	comments=all_data['Comments']
	rating=all_data["Manga's rating"]
	views=all_data["Manga's total views"]
	stars=analyze_comments(comments)
	print("\n")
	print("SA Rating: " + str(stars*2))
	print("Anime News Network Rating: "+ str(manga_rating))
	print("Manganelo Rating: " + str(rating[:3]))
	print("Total Manganelo Views: " + str(views))
	print("Total No. of comments: " + str(len(comments)))
	print("\n")
	
	SA.append(str(stars*2))
	ANN.append(str(manga_rating))
	MR.append(str(rating))
	manga_index.append(str(o_manga_name))
	total_views.append(str(views))
	total_comments.append(len(comments))
	
data={}
data.update({"SA Rating":SA})
data.update({"ANN Rating":ANN})
data.update({"MR Rating":MR})
data.update({"Manganelo Views",total_views})
data.update({"Total Comments",total_comments})
data.update({"manga index",manga_index})

df=pd.DataFrame(data,index=manga_index)
print(df)
df.to_csv('training_data.csv')

print("SCRAPING FAILED AT: ")
print(failed_attempts)	

print("TOTAL TIME:")
print(time.time()-start_time)
	






