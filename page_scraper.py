from bs4 import BeautifulSoup as BS
import time 
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service


from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from newsletter import final_post
#from summary import get_summary

def render_page(url):
        firefox_options = Options()
        firefox_options.add_argument('--headless')
        serv=Service('./geckodriver')
        driver=webdriver.Firefox(options=firefox_options,service=serv)
        try:
        	driver.get(url)
        except Exception as e:
        	print("Exception at driver.get() stage : "+str(e)+"\n")
        	return None
        	
        #-------------------------------------------------
		#SCRAPE BASIC INFO FROM TOP PANEL
        final_summary=scrape_summary(driver.page_source) 
        
        #-------------------------------------------------
		#EXPLICIT SLEEP SO IFRAME LOADS
        time.sleep(2) 
        
        #-------------------------------------------------
		#DRIVER FRAME SWITCHED
        WebDriverWait(driver, 20).until(EC.frame_to_be_available_and_switch_to_it((By.TAG_NAME,"iframe"))) #switch driver to iframe
        
        #-------------------------------------------------
		#ALL HIDDEN COMMENTS UNCOVERED
        load_all_comments(driver) 
        
        #-------------------------------------------------
		#PAGE SOURCE WITH UNCOVERED COMMENTS SENT TO MANGA_SCRAPER
        r = driver.page_source 
        driver.quit()
        return r,final_summary
 
 
 
 
def load_all_comments(driver):
	print("\n\n\nLOADING COMMENTS \n\n\n")
	
	#-------------------------------------------------
	#CURRENTLY DRIVER IS IN IFRAME SO IT'S SWITCHED TO DEFAULT AND SCROLLED
	driver.switch_to.default_content()
	driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
	
	#-------------------------------------------------
	#SWITCHING TO IFRAME AND CLICKING THE LOAD MORE BUTTON FIRST TIME
	WebDriverWait(driver, 20).until(EC.frame_to_be_available_and_switch_to_it((By.TAG_NAME,"iframe")))
	try:
		WebDriverWait(driver,20).until(EC.element_to_be_clickable((By.XPATH,"//button[@class='_1gl3 _4jy0 _4jy3 _517h _51sy _42ft']"))).click()
		while True:
			try :
		
				#-------------------------------------------------
				#SWITCHING TO DEFAULT DRIVER FRAME AND SCROLLING
				driver.switch_to.default_content()
				driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
				print("Scrolled Down")
			
				#-------------------------------------------------
				#SWITCHING TO IFRAME DRIVER AND CLICK THE "LOAD MORE COMMENTS BUTTON"
				WebDriverWait(driver, 20).until(EC.frame_to_be_available_and_switch_to_it((By.TAG_NAME,"iframe")))
				WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[@class='_1gl3 _4jy0 _4jy3 _517h _51sy _42ft']"))).click()
			
			except :
				print("\n\n\nNO COMMENTS LEFT\n\n\n")
				break
	except:
		print("\n\n\nLESS COMMENTS, NO NEED FOR SCROLLING\n\n\n")

def scrape_summary(page_source):
	soup = BS(page_source, "html.parser")
		
		#-------------------------------------------------
		#MANGA'S NAME
	try:
		manga_name=soup.find_all("div",{"class":"story-info-right"})[0].h1.text
		manga_name=manga_name.replace("\\","")
	except:
		manga_name=None
		
		#-------------------------------------------------
		#MANGA'S COVER IMAGE	
	try:
		manga_img=soup.find_all("span",{"class":"info-image"})[0].find("img",{"class":"img-loading"}).get('src')
	except:
		manga_img=None
		
		#-------------------------------------------------
		#CHECKING THE PRESENCE OF ALT TITLE	
	try:
		main_table=soup.find_all("table",{"class":"variations-tableInfo"})[0]
		check_alt=main_table.find_all("td",{"class":"table-label"})[0].text
		if(check_alt=="Alternative :"):
			alt=1
		else:
			alt=0
	except:
		pass
		
		#-------------------------------------------------
		#MANGA'S AUTHOR
	try:
		manga_author=main_table.find_all("td",{"class":"table-value"})[alt].find("a",{"class":"a-h"}).text
	except: 
		manga_author=None
		
		#-------------------------------------------------
		#MANGA'S CURRENT STATUS
	try:
		manga_status=soup.find_all("td",{"class":"table-value"})[alt+1].text
	except:
		manga_status=None 
		
		#-------------------------------------------------
		#MANGA'S GENRE
	try:
		manga_genre=soup.find_all("td",{"class":"table-value"})[alt+2].text
		manga_genre=manga_genre.replace("\n","")
		manga_genre=manga_genre.replace("\xa0","")
		manga_genre=manga_genre.replace("\\","")		
	except:
		manga_genre=None
		
		#-------------------------------------------------
		#MANGA'S RATING
	try:
		manga_rating=soup.find_all("em",{"id":"rate_row_cmd"})[0].text[21:]
		
	except:
		manga_rating=None

		#-------------------------------------------------
		#MANGA'S TOTAL VIEWS
	try:
		manga_views=soup.find_all("span",{"class":"stre-value"})[1].text
		
	except:
		manga_views=None

		
		#-------------------------------------------------
		#MANGA'S DESCRIPTION
	try:
		manga_desc=soup.find_all("div",{"class":"panel-story-info-description"})[0].text[14:]
		manga_desc=manga_desc.replace("\n","")
		manga_desc=manga_desc.replace("\xa0","")
		manga_desc=manga_desc.replace("\\","")
		#REMOVING SOFT HYPHENS
		manga_desc = manga_desc.replace('\xad', '') 
		manga_desc = manga_desc.replace('\u00ad', '')
		manga_desc = manga_desc.replace('\N{SOFT HYPHEN}', '')

	except:
		manga_desc=None
		
		#-------------------------------------------------
		#FINAL COMPILED SUMMARY IN DICTIONARY
		
	final_summary={"Manga's name":manga_name,"Manga's cover image":manga_img,"Manga's author(s)":manga_author,"Manga's current status": manga_status,"Manga's genre(s)":manga_genre,"Manga's total views":manga_views,"Manga's rating":manga_rating,"Manga's description":manga_desc}
	return final_summary
	     
			
def scrape_content_from_comments(all_comments):
	final_comments=[]
	final_images=[]
	
	for comment in all_comments:
		span_text=comment.find_all("span",{"class":"_5mdd"}) 
		
		#-------------------------------------------------
		#SCRAPING ALL COMMENTS (INCLUDING PARENT AND ALL CHILDREN NODES)
		flag=0
		for i in range(len(span_text)):
			comments_text=span_text[i].text

			#---------------------------------------------
			#BOTS TEND TO REDIRECT TO SOME THIRD PARTY URLS IN THE COMMENTS 
			#AND THOSE COMMENTS AND ASSOCIATED IMAGES ARE USELESS 
			if 'www' in comments_text.lower(): 
				flag=1
				break
			if 'http' in comments_text.lower(): 
				flag=1
				break
			if 'https' in comments_text.lower(): 
				flag=1
				break								
			comments_text=comments_text.replace("n\\","n")
			comments_text=comments_text.replace('\"','"')
			final_comments.append(comments_text)

		if flag==1:
			continue
		
		else:	
		#-------------------------------------------------
		#SCRAPING ALL IMAGES IN THE COMMENTS (INCLUDING PARENT AND ALL CHILDREN NODES)
			images=comment.find_all("a",{"class":"_2rn3 _4-eo"})
			for i in range(len(images)):
				img_src=images[i]['data-ploi']
				final_images.append(img_src)
	return final_comments,final_images
	
		

def compiled_info(url):
    r,final_summary = render_page(url)
    soup = BS(r, "html.parser")
    try:
    	all_comments = soup.find_all("div", {"class": "_3-8y _5nz1 clearfix"})
    except Exception as e:
    	print("Exception at manga_scraper"+str(e)+"\n")
    	return None
    comments,images=scrape_content_from_comments(all_comments)
    final_summary.update({"Manga's URL" : url})
    final_summary.update({"Comments": comments})
    final_summary.update({"Images": images})
    return final_summary
 
   

if __name__=="__main__":
	start_time=time.time()
	url="https://m.manganelo.com/manga-ns128438" #SAMPLE URL
	try:
		final_info=compiled_info(url)
		print(final_info)
	except Exception as e:
		print("Error encountered at url : {url} \n".format(url=url))
		print(e)
	final_post(final_info)
	print("\n")
	#get_summary(manga_desc)
	print(time.time() - start_time)






