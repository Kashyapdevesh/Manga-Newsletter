import sys
import threading
from queue import Queue
import json
import datetime
import dateutil.relativedelta
import pandas as pd
import requests
from bs4 import BeautifulSoup

final_info_dict={}

final_manga_list=[]
updated_info={}

queue = Queue()
NUMBER_OF_THREADS = 100

pages_crawled=[]
manga_crawled=[]
single_page=False

failed_pages=[]

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
                final_info_dict[inputid]=manga_info
                manga_crawled.append(inputid)
                print(str(threading.current_thread().name) + " has completed crawling - " + str(inputid) + '\n\n')
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
    
    manga_blocks=soup.find_all("a",{"class":"genres-item-name text-nowrap a-h"})
    page_manga_list=[manga_url['href'] for manga_url in manga_blocks]

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

def get_page_count():
    lo,high,page_count=0,1000,0

    today=datetime.datetime.today()
    target_date=(today+dateutil.relativedelta.relativedelta(days=-7)).strftime("%d-%m-%y")

    while lo <=high:

        mid=(lo+high)//2
        
        soup=render_page(f"https://m.manganelo.com/genre-all/{mid}")
        date_string=soup.find_all("span",{"class":"genres-item-time"})[0].text
        page_date=datetime.datetime.strptime(date_string, "%b %d,%y").strftime("%d-%m-%y")

        if page_date==target_date:
            return mid
        
        elif page_date < target_date:
            high = mid - 1
        else:
            lo = mid + 1
    return -1

def get_updated_data(url):

    soup=render_page(url)
    if not soup:
        return None

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
        manga_genre=soup.find_all("td",{"class":"table-value"})[alt+2].text
        manga_genre=manga_genre.replace("\n","")
        manga_genre=manga_genre.replace("\xa0","")
        manga_genre=manga_genre.replace("\\","")		
    except:
        manga_genre=None
        
    try:
        rating_block=soup.find_all("em",{"id":"rate_row_cmd"})[0].text
        manga_rating=rating_block[rating_block.find(":")+2:]
        
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
            index_info = {f"{chapter_text.text}": {"chapter_views":chapter_view.text,"chapter_upload_date":chapter_update_date.text} for chapter_text, chapter_view, chapter_update_date in zipped_data}
        else:
            index_info={}
    except:
        index_info={}
        
    final_summary={"Name":manga_name,"Cover Image":manga_img,"Author":manga_author,
                   "Current Status": manga_status,"Manga Genre":manga_genre,"Manga Total Views":manga_views,
                   "Rating":manga_rating,"Description":manga_desc,"chapters_info":index_info}
    return final_summary
	 
 
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

def get_updated_manga_url():
    global queue
    global pages_crawled
    global single_page

    single_page=False

    input_pagelist=[f"https://m.manganelo.com/genre-all/{val}" for val in range(get_page_count())]

    print(f"\n{len(input_pagelist)} PAGES UPDATED\n")

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

    print("\nCHECKING MANGA UPDATED IN PAST WEEK\n")
    print("------------------------------------")

    updated_manga_count=get_updated_manga_url()

    print(f"\n{updated_manga_count} MANGA UPDATED IN PAST WEEK\n")

    print("\n\n\nCRAWLING UPDATED MANGA\n")
    print("------------------------")

    crawl_mangalist()

    print("\nALL MANGA INFORMATION SUCCESSFULLY CRAWLED\n")
    print("---------------------------------------------")

    print("\n\n\nnWRITING DATA TO FILE\n")
    print("---------------------")

    with open('final_data.txt', 'w+') as final_info_file:
        final_info_file.write(json.dumps(final_info_dict))

    print("DATA SUCCESSFULLY WRITTEN\n")

    # print('\nALL DATES CRAWLED\n')
    # print("\nCRAWLING COMPLETED SUCCESSFULLY\n")
    # logger_dict['success'].append('INFO:WIPO Delisted: All dates successfully crawled')

    # if len(failed_dates)>0:
    #     print (f"\nDATES WITH ERRORS AND NUMBER OF ATTEMPTS : {failed_dates}\n")

    # print("\nUploading Audit file to ADLS\n")

    # df=pd.read_csv("./WIPO_delisted_date_verification.csv")
    # Execute.upload_file("WIPO_delisted_date_verification.csv",df.to_csv(index=False),view_filepath)
    

    # try:
    #     os.remove("./WIPO_delisted_date_verification.csv")
    #     os.remove("./authenticated_proxy_plugin5.zip")
    # except:
    #     pass

    # runtime=datetime.datetime.now()-startTime
    # print(f"\nTOTAL TIME TAKEN : {runtime} on {today}\n")

    # print("Generating HTML report and updating activity log")

    # #Generating HTML report and updating activity log
    # content = {'source': 'WIPO-DELISTED', 'current_date': f"{datetime.datetime.now().strftime('%H:%M:%S %Y-%b-%d')}", 'runtime': round(((runtime.total_seconds()) / 60),5), 'environment': 'azure', 'final_status': 'success', 'logger': logger_dict,'sucess_count':total_records}
    # generate_html_report(report_name='WIPO-DELISTED',content=content,acc_url=acc_url,credential=creds)

    # update_log(runtime,total_records)

    # print("Log updated and report created")

    sys.exit(0)
