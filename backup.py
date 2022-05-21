from bs4 import BeautifulSoup as BS
import time 
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By


def render_page(url):
        firefox_options = Options()
        firefox_options.add_argument('--headless')
        driver=webdriver.Firefox(options=firefox_options)
        driver.get(url)
        scrape_summary(driver.page_source)
        time.sleep(2)
        iframeElement = driver.find_element(by=By.TAG_NAME, value='iframe')
        driver.switch_to.frame(iframeElement)
        r = driver.page_source
        driver.quit()
        return r
 
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
	     
			
def scrape_content_from_comments(all_comments):
	final_comments=[]
	final_images=[]
	for comment in all_comments:
		main_text=comment.find_all("span",{"class":"_5mdd"}) 
		images=comment.find_all("a",{"class":"_2rn3 _4-eo"})
		for i in range(len(main_text)):
			comments_text=main_text[i].text
			final_comments.append(comments_text)
		for i in range(len(images)):
			img_src=images[i]['data-ploi']
			final_images.append(img_src)
	return final_comments,final_images
	
	

def manga_scraper(url):
    r = render_page(url)
    soup = BS(r, "html.parser")
    all_comments = soup.find_all("div", {"class": "_3-8y _5nz1 clearfix"})
    comments,images=scrape_content_from_comments(all_comments)
    print(comments)
    print(images)
    return soup
      

if __name__=="__main__":
	start_time=time.time()
	soup=manga_scraper("https://m.manganelo.com/manga-ka125246")
	print(time.time() - start_time)
	print((time.time() - start_time)/60)






