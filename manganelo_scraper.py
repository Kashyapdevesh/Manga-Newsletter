import sys
import threading
from queue import Queue
import re
import datetime
import dateutil.relativedelta
import pandas as pd
import json
import requests
from bs4 import BeautifulSoup
import tempfile
import os
import subprocess

final_info_dict={}

final_manga_list=[]
updated_info={}

queue = Queue()
NUMBER_OF_THREADS = 5

pages_crawled=[]
manga_crawled=[]
single_page=False

failed_pages=[]
failed_manga=[]
'''
Create worker threads (will die when main exits)
'''
def create_workers():
    global NUMBER_OF_THREADS
    for _ in range(NUMBER_OF_THREADS):
        t = threading.Thread(target=work)
        t.daemon = True
        t.start()

'''
Do the next job in the queue
'''

def work():
    global queue
    global final_manga_list
    global final_info_dict
    global single_page
    global failed_pages

    while True:
        inputid = queue.get()
        print(str(threading.current_thread().name) + " is now crawling - " + str(inputid))
        
        try:
            if single_page==True:
                manga_info=get_updated_data(url=inputid)
                if manga_info:
                    final_info_dict[inputid]=manga_info
                    manga_crawled.append(inputid)
                    print(str(threading.current_thread().name) + " has completed crawling - " + str(inputid) + '\n\n')
                else:
                    print(str(threading.current_thread().name) + " encountered error while crawling - " + str(inputid) + '\n\n')
                    failed_manga.append(inputid)
            else:
                page_manga_list=generate_manga_list(url=inputid)
                if not page_manga_list:
                    print(str(threading.current_thread().name) + " encountered error while crawling - " + str(inputid) + '\n\n')
                    failed_pages.append(inputid)
                    # queue.put(str(inputid))
                else:
                    final_manga_list.extend(page_manga_list)
                    pages_crawled.append(inputid)
                    print(str(threading.current_thread().name) + " has completed crawling - " + str(inputid) + '\n\n')
    
        except Exception as e:
            error_msg=str(e)
            print(error_msg)

        queue.task_done()

'''
Each queued link is a new job
'''

def create_jobs(input_list):
    for inputid in input_list:
        queue.put(str(inputid))
    queue.join()

'''
Check if there are items in the queue, if so crawl them
'''
def crawl(input_list):
    if len(input_list) > 0:
        print(str(len(input_list)+ int(queue.qsize())) + ' inputs in the queue')
        create_jobs(input_list)

def generate_manga_list(url):
    soup=render_page(url)
    if not soup:
        return None
    
    manga_blocks=soup.find_all("div",{"class":"list-truyen-item-wrap"})
    page_manga_list=[manga_url.find_all("a")[0]['href'] for manga_url in manga_blocks]

    return list(set(page_manga_list))


def render_page(url):
    soup=None
    try:
        page_content=requests.get(url).text
        soup=BeautifulSoup(page_content,"html.parser")
    except Exception as e:
        print(f"Error while rendering page for {url}")
        print(str(e))
    return soup

def scrape_manganato(soup):

    try:
        manga_name=soup.find_all("div",{"class":"story-info-right"})[0].h1.text
        manga_name=manga_name.replace("\\","")
    except:
        manga_name=None
        
    try:
        manga_img=soup.find_all("span",{"class":"info-image"})[0].find("img",{"class":"img-loading"}).get('src')
    except:
        manga_img=None

    #check presence of alternative manga title column   
    try:
        main_table=soup.find_all("table",{"class":"variations-tableInfo"})[0]
        check_alt=main_table.find_all("td",{"class":"table-label"})[0].text
        if(check_alt=="Alternative :"):
            alt=1
        else:
            alt=0
    except:
        pass
        
    try:
        manga_author=main_table.find_all("td",{"class":"table-value"})[alt].find("a",{"class":"a-h"}).text
    except: 
        manga_author=None
        
    try:
        manga_status=soup.find_all("td",{"class":"table-value"})[alt+1].text
    except:
        manga_status=None 
        
    try:
        manga_genre=str(soup.find_all("td",{"class":"table-value"})[alt+2].text).replace("-",",")
        manga_genre=manga_genre.replace("\n","")
        manga_genre=manga_genre.replace("\xa0","")
        manga_genre=manga_genre.replace("\\","")		
    except:
        manga_genre=None
        
    try:
        rating_block=soup.find_all("em",{"id":"rate_row_cmd"})[0].text
        manga_rating=str(rating_block[rating_block.find(":")+2:]).replace("\n","")
        
    except:
        manga_rating=None

    try:
        manga_views=soup.find_all("span",{"class":"stre-value"})[1].text
        
    except:
        manga_views=None

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

    try:
        chapter_texts=soup.find_all("a",{"class":"chapter-name text-nowrap"})
        chapter_views=soup.find_all("span",{"class":"chapter-view text-nowrap"})
        chapter_update_dates=soup.find_all("span",{"class":"chapter-time text-nowrap"})

        if len(chapter_texts) == len(chapter_views) == len(chapter_update_dates):
            zipped_data=zip(chapter_texts,chapter_views,chapter_update_dates)
            index_info = {f"{chapter_text.text}": {"chapter_views":chapter_view.text,"chapter_upload_date":chapter_update_date['title']} for chapter_text, chapter_view, chapter_update_date in zipped_data}
        else:
            index_info={}
    except:
        index_info={}
        
    final_summary={"Name":manga_name,"Cover Image":manga_img,"Author":manga_author,
                   "Current Status": manga_status,"Manga Genre":manga_genre,"Manga Total Views":manga_views,
                   "Rating":manga_rating,"Description":manga_desc,"chapters_info":index_info}
    return final_summary

def scrape_mangakaklot(soup):

    try:
        info_block=soup.find_all("ul",{"class":"manga-info-text"})[0]
        manga_name=info_block.find_all("li")[0].h1.text
        manga_name=manga_name.replace("\\","")
    except:
        manga_name=None
        
    try:
        manga_img=soup.find_all("div",{"class":"manga-info-pic"})[0].img.get('src')
    except:
        manga_img=None
        
    try:
        info_block=soup.find_all("ul",{"class":"manga-info-text"})[0]
        manga_author=str(info_block.find_all("li")[1].text).replace("\n","").split(":")[-1].replace(" ","")
    except: 
        manga_author=None
        
    try:
        info_block=soup.find_all("ul",{"class":"manga-info-text"})[0]
        manga_status=str(info_block.find_all("li")[2].text).replace("\n","").split(":")[-1].replace(" ","")
    except:
        manga_status=None 
        
    try:
        info_block=soup.find_all("ul",{"class":"manga-info-text"})[0]
        manga_genre=str(info_block.find_all("li")[6].text).replace("\n","").split(":")[-1]
        manga_genre=manga_genre.replace("\n","")
        manga_genre=manga_genre.replace("\xa0","")
        manga_genre=manga_genre.replace("\\","")
    except:
        manga_genre=None
        
    try:
        info_block=soup.find_all("ul",{"class":"manga-info-text"})[0]
        manga_rating=str(info_block.find_all("li")[8].em.text).replace("\n","").split(":")[-1]
        
    except:
        manga_rating=None

    try:
        info_block=soup.find_all("ul",{"class":"manga-info-text"})[0]
        manga_views=str(info_block.find_all("li")[5].text).replace("\n","").split(":")[-1].replace(" ","").replace(",","")
    except:
        manga_views=None

    try:
        manga_desc=soup.find_all("div",{"id":"noidungm"})[0].text
        manga_desc=manga_desc.replace("\n","")
        manga_desc=manga_desc.replace("\xa0","")
        manga_desc=manga_desc.replace("\\","")
        #REMOVING SOFT HYPHENS
        manga_desc = manga_desc.replace('\xad', '') 
        manga_desc = manga_desc.replace('\u00ad', '')
        manga_desc = manga_desc.replace('\N{SOFT HYPHEN}', '')

    except:
        manga_desc=None

    try:
        chapter_block=soup.find_all("div",{"class":"chapter-list"})[0].find_all("div",{"class":"row"})

        index_info={}
        for chapter in chapter_block:
            chapter_text=chapter.find_all("span")[0].text
            chapter_views=chapter.find_all("span")[1].text
            chapter_upload_date=chapter.find_all("span")[2]['title']

            index_info[chapter_text]={'chapter_views': chapter_views, 'chapter_upload_date': chapter_upload_date}
    except:
        index_info={}
    
    # try:
    #     ap_summary=anime_planet_scraper(manga_name)
    # except:
    #     ap_summary=[" "]*7
        
    final_summary={"Name":manga_name,"Cover Image":manga_img,"Author":manga_author,
                    "Current Status": manga_status,"Manga Genre":manga_genre,"Manga Total Views":manga_views,
                    "Rating":manga_rating,"Description":manga_desc,"chapters_info":index_info}
    return final_summary

def anime_planet_scraper(manga_name):
    manga_name=manga_name[:manga_name.find("[")-1] if "[" in manga_name else manga_name
    manga_name=manga_name.replace("-"," ")
    manga_name=re.sub(r"[^\w\s]", "", manga_name)
    manga_name=manga_name.lower().replace("  "," ").replace(" ","-")

    url=f"https://www.anime-planet.com/manga/{manga_name}"

    content=requests.get(url).text

    blocked_keywords=["but we couldn't find anything","can't find what you're looking for"]
    if any(ele in content.lower() for ele in blocked_keywords):
        return [" "]*7

    soup=BeautifulSoup(content,"html.parser")

    try:
        nav_bar=soup.find("section",{"class":"pure-g entryBar"})
        publishing_studio=nav_bar.find_all("div",{"class":"pure-1 md-1-5"})[1].a.text
    except:
        publishing_studio=""

    try:
        nav_bar=soup.find("section",{"class":"pure-g entryBar"})
        publishing_year=nav_bar.find_all("div",{"class":"pure-1 md-1-5"})[2].span.text
    except:
        publishing_year=""
    
    try:
        nav_bar=soup.find("section",{"class":"pure-g entryBar"})
        user_rating=nav_bar.find_all("div",{"class":"pure-1 md-1-5"})[3].div['title']

        parts = user_rating.split()
        rating = parts[0]
        votes = parts[-2]

        user_rating = f"{rating.replace(' out of ', '/')}- {str(votes).replace(',','')}"
    except:
        user_rating=""
    
    try:
        nav_bar=soup.find("section",{"class":"pure-g entryBar"})
        rank=nav_bar.find_all("div",{"class":"pure-1 md-1-5"})[4].text.replace(",","")

        match = re.search(r'\d+', rank)
        if match:
            rank = match.group()
        else:
            rank=""

    except:
        rank=""
    
    try:
        side_bar=soup.find("section",{"class":"sidebarStats"})
        tracking_count=side_bar.text.replace(",","")

        match = re.search(r'\d+', tracking_count)
        if match:
            tracking_count = match.group()
        else:
            tracking_count=""
    except:
        tracking_count=""
    
    try:
        ap_desc=soup.find("div",{"class":"synopsisManga"}).p.text
        ap_desc=ap_desc.replace("\n","")
        ap_desc=ap_desc.replace("\xa0","")
        ap_desc=ap_desc.replace("\\","")
    except:
        ap_desc=""

    try:
        ap_cover_img=soup.find("div",{"class":"mainEntry"}).img['src']
    except:
        ap_cover_img=""

    return [publishing_studio,publishing_year,user_rating,rank,tracking_count,ap_desc,ap_cover_img]


def get_updated_data(url):

    soup=render_page(url)
    if not soup:
        return None
    
    if soup.find_all("meta",{"name":"Author"}):
        return scrape_manganato(soup)
    else:
        return scrape_mangakaklot(soup)

	 
 
def crawl_mangalist():
    global queue
    global final_manga_list
    global manga_crawled
    global single_page

    single_page=True

    input_mangalist=final_manga_list

    queue.put(input_mangalist[0])
    input_mangalist=input_mangalist[1:] if len(input_mangalist)>1 else []

    while not (queue.empty()):
        print('Pages Left : ' + str(len(input_mangalist)+1))

        create_workers()
        crawl(input_mangalist)

        '''
        check for uncrawled manga  
        '''
        manga_crawled=list(set(manga_crawled))
        input_mangalist = [i for i in input_mangalist if i not in manga_crawled]

    return len(final_manga_list)

def get_page_count():
    lo,high,page_count=0,1000,0

    today=datetime.datetime.today()
    target_date=(today+dateutil.relativedelta.relativedelta(days=-7)).strftime("%y-%m-%d")

    while lo <=high:
        mid=(lo+high)//2
        print(mid)
        
        soup=render_page(f'https://mangakakalot.com/manga_list?type=latest&category=all&state=all&page={mid}')
        redirected_url_block=soup.find_all("div",{"class":"list-truyen-item-wrap"})[0]
        redirected_url=redirected_url_block.find_all("a")[0]['href']

        print(redirected_url)
        manga_resp_soup=render_page(redirected_url)

        if manga_resp_soup.find_all("meta",{"name":"Author"}):
            date_string=manga_resp_soup.find_all("span",{"class":"stre-value"})[0].text
            date_string=date_string[:date_string.find("-")-1]
        else:
            date_string=manga_resp_soup.find("ul",{"class":"manga-info-text"}).find_all("li")[3].text
            
            parts = date_string.split()
            month, day, year = parts[3].split('-')
            date_string = f"{month} {day},{year}"

        print(date_string)
        print()


        # date_string=
        page_date=datetime.datetime.strptime(date_string, "%b %d,%Y").date().strftime("%y-%m-%d")

        if page_date==target_date:
            return mid
        
        elif page_date < target_date:
            high = mid - 1
        else:
            lo = mid + 1
    return -1


def get_updated_manga_url():
    global queue
    global pages_crawled
    global single_page

    single_page=False

    input_pagelist=[f"https://mangakakalot.com/manga_list?type=latest&category=all&state=all&page={val}" for val in range(get_page_count())]
    
    print(f"\n{len(input_pagelist)} PAGES UPDATED\n")
    print(input_pagelist)
    queue.put(input_pagelist[0])
    input_pagelist=input_pagelist[1:] if len(input_pagelist)>1 else []

    while not (queue.empty()):
        print('Pages Left : ' + str(len(input_pagelist)+1))

        create_workers()
        crawl(input_pagelist)

        '''
        check for uncrawled pages  
        '''
        pages_crawled=list(set(pages_crawled))
        input_pagelist = [i for i in input_pagelist if i not in pages_crawled]
    
    if len(failed_pages)>0:
        print(f"Failed to get following pages : {failed_pages}")

    return len(final_manga_list)



if __name__=="__main__":

    start=datetime.datetime.now()

    print("\nCHECKING MANGA UPDATED IN PAST WEEK\n")
    print("------------------------------------")

    updated_manga_count=get_updated_manga_url()

    print(f"\n{updated_manga_count} MANGA UPDATED IN PAST WEEK\n")


    print("\n\nCRAWLING UPDATED MANGA")
    print("------------------------")

    crawl_mangalist()
    print("\nALL MANGA INFORMATION SUCCESSFULLY CRAWLED")
    print("---------------------------------------------")

    print("\nWRITING DATA TO FILE")
    print("---------------------")


    # Create a temporary directory with a unique name
    final_info_file = tempfile.mkdtemp(prefix='final_data_directory')

    # Create a temporary file inside the directory
    temp_file_path = os.path.join(final_info_file, 'final_data_file.json')

    with open(temp_file_path, 'w') as temp_file:
        json.dump(final_info_dict, temp_file)
    
    print("DATA SUCCESSFULLY WRITTEN")


    print((datetime.datetime.now()-start))

    subprocess.call(['python', 'postprocessing.py', final_info_file])

