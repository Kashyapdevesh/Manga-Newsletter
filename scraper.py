import pandas as pd
from bs4 import BeautifulSoup as BS
from functools import reduce

import time 
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By


def load_all_comments(driver):
	driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
	#driver.find_elements_by_xpath("//button[@title='Load 10 more comments']")[0].click()
	print(driver.find_elements(by=By.XPATH, value='/html/body/div/div/div/div/div/div[3]/div[20]/button'))		


def render_page(url):
        firefox_options = Options()
        #firefox_options.add_argument('--headless')
        #firefox_options.add_argument('--disable-gpu')
        driver=webdriver.Firefox(options=firefox_options)
        driver.get(url)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        time.sleep(5)
        iframeElement = driver.find_element(by=By.TAG_NAME, value='iframe')
        driver.switch_to.frame(iframeElement)
        load_all_comments(driver)
        r = driver.page_source
        driver.quit()
        return r
      
  
def hourly_scraper(url):
    r = render_page(url)
    soup = BS(r, "html.parser")
    return soup
    

if __name__=="__main__":
	soup=hourly_scraper("https://chap.manganelo.com/manga-ni89902")
	print(soup.prettify())
	print("\n\n FINISH \n\n")


