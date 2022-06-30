from bs4 import BeautifulSoup as BS
from requests import get
import re
import csv
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

failed_attempts=[]

time_index=1
total_diff=0
count=1


field_names=['Manga Index','SA Rating','ANN Rating','MR Rating','Manganelo Views','Total Comments']

#with open('Manga.csv','w') as csvfile:
#	writer = csv.DictWriter(csvfile, fieldnames=field_names)
#	writer.writeheader()
#	csvfile.close()
#
#print("EMPTY CSV CREATED \n\n")

def write_csv(field_values):
	
	with open('Manga.csv','a') as csvfile:
		dictwriter_object = csv.DictWriter(csvfile, fieldnames=field_names)
		dictwriter_object.writerow(field_values)
		csvfile.close()

def read_csv():
	manga_list=[]
	df=pd.read_csv("./Manga.csv")
	manga=df[df.columns[0]].to_numpy()
	manga_list=manga.tolist()
	return manga_list
	
scraped_manga=read_csv()
print(scraped_manga)

for manga in mangas:
	o_manga_name=manga.find_all("td",{"class":"t"})[0].text
	if o_manga_name in scraped_manga:
		print("Already scraped: " + str(o_manga_name)+"\n")
		continue
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
		print(str(manga_name) + " not available- DATA COMPILATION FAILED\n")
		print("-----------------------------------------------")
		print(e)
		continue
		
	comments=all_data['Comments']
	rating=all_data["Manga's rating"]
	views=all_data["Manga's total views"]
	stars=analyze_comments(comments)
	if stars == None:
		failed_attempts.append(manga_name)
		print("GOING TO SLEEP FOR")
		print(1 * time_index)
		time.sleep(1*time_index)
		time_index+=1
		continue
	print("\n")
	print("SA Rating: " + str(stars*2))
	print("Anime News Network Rating: "+ str(manga_rating))
	print("Manganelo Rating: " + str(rating[:3]))
	print("Total Manganelo Views: " + str(views))
	print("Total No. of comments: " + str(len(comments)))
	print("\n")
	
	total_diff+=abs(float(manga_rating)/float(stars*2))
	print("\n")
	print("Total diff: " +str(total_diff))
	print("Total count: " +str(count))
	print(time.time()-start_time)
	print("\n")
	count+=1
		
	field_values={'Manga Index':str(o_manga_name),
				  'SA Rating':float(stars*2),
				  'ANN Rating':float(manga_rating),
				  'MR Rating':str(rating[:3]),
				  'Manganelo Views':str(views),
				  'Total Comments':int(len(comments))}
	
	write_csv(field_values)
	print("CSV updated with :"+ str(o_manga_name)+"\n")
	

print("SCRAPING FAILED AT: ")
print(failed_attempts)	

print("TOTAL TIME:")
print(time.time()-start_time)
	






