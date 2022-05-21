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
        #firefox_options.add_argument('--headless')
        driver=webdriver.Firefox(options=firefox_options)
        driver.get(url)
        scrape_summary(driver.page_source) #scrape basic info from top panel
        time.sleep(2)
        WebDriverWait(driver, 20).until(EC.frame_to_be_available_and_switch_to_it((By.TAG_NAME,"iframe")))
        load_all_comments(driver) # open all hidden comments
        r = driver.page_source
        driver.quit()
        return r
  

      
def scrape_comments(all_comments):
	final_comments=[]
	for comment in all_comments:
		main_text=comment.find_all("span",{"class":"_5mdd"}) 
		for i in range(len(main_text)):
			comments_text=main_text[i].text
			final_comments.append(comments_text)
	return final_comments

		
def scrape_images(all_comments):
	final_images=[]
	for comment in all_comments:
		images=comment.find_all("a",{"class":"_2rn3 _4-eo"})
		for i in range(len(images)):
			img_src=images[i]['data-ploi']
			final_images.append(img_src)
	return final_images
		
def scrape_summary(page_source):
	soup = BS(page_source, "html.parser")
	manga_name=soup.find_all("div",{"class":"story-info-right"})[0].h1.text
	manga_img=soup.find_all("span",{"class":"info-image"})[0].find("img",{"class":"img-loading"}).get('src')
	manga_author=soup.find_all("td",{"class":"table-value"})[1].find("a",{"class":"a-h"}).text
	manga_status=soup.find_all("td",{"class":"table-value"})[2].text
	manga_genre=soup.find_all("td",{"class":"table-value"})[3].text
	manga_rating=soup.find_all("em",{"id":"rate_row_cmd"})[0].text[21:]
	manga_desc=soup.find_all("div",{"class":"panel-story-info-description"})[0].text[14:]
	final_summary={"Manga's Name":manga_name,"Manga's cover Image":manga_img,"Manga's author(s)":manga_author,"Manga's current status": manga_status,"Manga's genre(s)":manga_genre,"Manga rating":manga_rating,"Manga description":manga_desc}
	print(final_summary)
	#return final_summary
	
def load_all_comments(driver):
	print("\n\n\n LOADING COMMENTS \n\n\n")
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
			print("NO COMMENTS LEFT")
			break

def manga_scraper(url):
    r = render_page(url)
    soup = BS(r, "html.parser")
    all_comments = soup.find_all("div", {"class": "_3-8y _5nz1 clearfix"})
    comments=scrape_comments(all_comments)
    images=scrape_images(all_comments)
    print(comments)
    print(images)
    return soup
      

if __name__=="__main__":
	start_time=time.time()
	soup=manga_scraper("https://m.manganelo.com/manga-ka125246")
	print(time.time() - start_time)
	print((time.time() - start_time)/60)





