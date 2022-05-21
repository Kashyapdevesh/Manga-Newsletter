from bs4 import BeautifulSoup as BS
import time 
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


def render_page(url):
        firefox_options = Options()
        firefox_options.add_argument('--headless')
        driver=webdriver.Firefox(options=firefox_options)
        try:
        	driver.get(url)
        except Exception as e:
        	print("Exception at driver.get() stage"+str(e)+"\n")
        	return None
        final_summary=scrape_summary(driver.page_source) #scrape basic info from top panel
        time.sleep(2) # explicit sleep so iframe loads
        WebDriverWait(driver, 20).until(EC.frame_to_be_available_and_switch_to_it((By.TAG_NAME,"iframe"))) #switch driver to iframe
        load_all_comments(driver) # open all hidden comments
        r = driver.page_source #new page source with all comments uncovered sent to manga_scraper
        driver.quit()
        return r,final_summary
 
 
def load_all_comments(driver):
	print("\n\n\nLOADING COMMENTS \n\n\n")
	driver.switch_to.default_content()
	driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
	WebDriverWait(driver, 20).until(EC.frame_to_be_available_and_switch_to_it((By.TAG_NAME,"iframe")))
	driver.find_element(by=By.XPATH, value="//button[@class='_1gl3 _4jy0 _4jy3 _517h _51sy _42ft']").click()
	while True:
		try :
			driver.switch_to.default_content()
			driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
			print("Scrolled Down")
			WebDriverWait(driver, 20).until(EC.frame_to_be_available_and_switch_to_it((By.TAG_NAME,"iframe")))
			WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[@class='_1gl3 _4jy0 _4jy3 _517h _51sy _42ft']"))).click()
		except :
			print("\n\n\nNO COMMENTS LEFT\n\n\n")
			break

def scrape_summary(page_source):
	soup = BS(page_source, "html.parser")
	try:
		manga_name=soup.find_all("div",{"class":"story-info-right"})[0].h1.text
		manga_name=manga_name.replace("\\","")
	except:
		manga_name=None
	try:
		manga_img=soup.find_all("span",{"class":"info-image"})[0].find("img",{"class":"img-loading"}).get('src')
	except:
		manga_img=None
	try:
		manga_author=soup.find_all("td",{"class":"table-value"})[1].find("a",{"class":"a-h"}).text
	except:
		manga_author=None
	try:
		manga_status=soup.find_all("td",{"class":"table-value"})[2].text
	except:
		manga_status=None
	try:
		manga_genre=soup.find_all("td",{"class":"table-value"})[3].text
		manga_genre=manga_genre.replace("\n","")
		manga_genre=manga_genre.replace("\xa0","")
		manga_genre=manga_genre.replace("\\","")		
	except:
		manga_genre=None
	try:
		manga_rating=soup.find_all("em",{"id":"rate_row_cmd"})[0].text[21:]
		
	except:
		manga_rating=None
	try:
		manga_desc=soup.find_all("div",{"class":"panel-story-info-description"})[0].text[14:]
		manga_desc=manga_desc.replace("\n","")
		manga_desc=manga_desc.replace("\xa0","")
		manga_desc=manga_desc.replace("\\","")
	except:
		manga_desc=None
	final_summary={"Manga's Name":manga_name,"Manga's cover Image":manga_img,"Manga's author(s)":manga_author,"Manga's current status": manga_status,"Manga's genre(s)":manga_genre,"Manga rating":manga_rating,"Manga description":manga_desc}
	return final_summary
	     
			
def scrape_content_from_comments(all_comments):
	final_comments=[]
	final_images=[]
	for comment in all_comments:
		main_text=comment.find_all("span",{"class":"_5mdd"}) 
		images=comment.find_all("a",{"class":"_2rn3 _4-eo"})
		for i in range(len(main_text)):
			comments_text=main_text[i].text
			comments_text=comments_text.replace("n\\","n")
			final_comments.append(comments_text)
		for i in range(len(images)):
			img_src=images[i]['data-ploi']
			final_images.append(img_src)
	return final_comments,final_images
	
	

def manga_scraper(url):
    r,final_summary = render_page(url)
    soup = BS(r, "html.parser")
    try:
    	all_comments = soup.find_all("div", {"class": "_3-8y _5nz1 clearfix"})
    except Exception as e:
    	print("Exception at manga_scraper"+str(e)+"\n")
    	return None
    comments,images=scrape_content_from_comments(all_comments)
    return comments,images,final_summary
      

if __name__=="__main__":
	start_time=time.time()
	url="https://chap.manganelo.com/manga-mb127247"
	try:
		comments,images,final_summary=manga_scraper(url)
		print(final_summary)
		print(comments)
		print(images)
	except Exception as e:
		print("None value received for soup at url :{} \n",url)
		print(e)
	print(time.time() - start_time)
	print((time.time() - start_time)/60)






