from bs4 import BeautifulSoup as BS
import time 
from requests import get
import json

from page_scraper import compiled_info

def render_page(url):
	try:
		r=get(url)
		soup=BS(r.text,"html.parser")
	except Exception as e:
		print("Error while rendering page")
		print(e)
		return None
	return soup	


def title_link_scraper(soup,index):
	manga=soup.find_all("div",{"class":"content-homepage-item"})[index]
	if manga!=None:
		try:
			manga_title=manga.find_all("div",{"class":"content-homepage-item-right"})[0].h3.text
			manga_title=manga_title.replace("\n","")
		except Exception as e:
			print("manga title unavailiable")
			print(e)
			manga_title=None
		
		try:	
			manga_link=manga.find_all("div",{"class":"content-homepage-item-right"})[0].h3.a['href']
		except Exception as e:
			print("manga link unavailable")
			print(e)
			manga_link=None
	return manga_title,manga_link
	




def collect_new_manga(soup,prev_manga_title):
	manga_index=soup.find_all("div",{"class":"content-homepage-item"})
	final_result={}
	index=0
	for i in range(len(manga_index)):
		curr_manga_title,curr_manga_link=title_link_scraper(soup,i)
		
		if curr_manga_title == None or curr_manga_link==None:
			print("Error while fetching updated manga details")
			
		else:
			if curr_manga_title == prev_manga_title:
				print("----------------All updated manga(s) collected----------------- \n\n\n")
				break
			else:
				print("\n{manga_title} added\n".format(manga_title=curr_manga_title))
				scraped_content =compiled_info(curr_manga_link)
				final_result.update({index:scraped_content})
				index+=1
	save_info(final_result)
		
	

def save_info(final_result):
	with open("sample.json" ,"w") as output_file:
		json.dump(final_result,output_file)
	
	
	

def manga_scraper(url):
	#Initiation
	soup=render_page(url)
	if soup!=None:
		prev_manga_title,prev_manga_link=title_link_scraper(soup,index=0)
		if prev_manga_title==None or prev_manga_link==None:
			print("Error while scraping for link and title at Initiation stage")
			return None
	else:
		print("Page rendering failed at Initiation stage")
		return None
	time.sleep(10)
	
	#Repetition
	while True:
		soup=render_page(url)
		if soup!=None:
			curr_manga_title,_=title_link_scraper(soup,index=0)
			if curr_manga_title==None:
				print("Error while scraping for title at Repetition stage")
				break
		else:
			print("Page rendering failed at Repetion Stage")
			break
		
		if curr_manga_title == prev_manga_title:
			print("No new manga added")
			time.sleep(10)
			continue
		else:
			print("\n\nNew manga(s) added\n\n")
			print("\n\nCollecting information about new manga(s)\n\n")
			collect_new_manga(soup,prev_manga_title)
			prev_manga_title = curr_manga_title
			time.sleep(10)



if __name__=="__main__":
	start_time=time.time()
	url="https://m.manganelo.com/www" 
	try:
		print(manga_scraper(url))
	except Exception as e:
		print(e)
	print(time.time() - start_time)






