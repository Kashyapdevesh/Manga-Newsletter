import pandas as pd
from bs4 import BeautifulSoup as BS
from functools import reduce

import time 
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
import random

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def render_page(url):
        firefox_options = Options()
        #firefox_options.add_argument('--headless')
        #firefox_options.add_argument('--disable-gpu')
        driver=webdriver.Firefox(options=firefox_options)
        driver.get(url)
        try:
        		element=WebDriverWait(driver, 10).until(
        			EC.presence_of_element_located((By.CLASS_NAME,"_4k-6")))
        		print("element found")
        	except:
        	 return None
        time.sleep(3)
        r = driver.page_source
        driver.quit()
        return r
        
def hourly_scraper(url):
    r = render_page(url)
    soup = BS(r, "html.parser")
    return soup
    
soup=hourly_scraper("https://chap.manganelo.com/manga-ni89902")
print(soup)
