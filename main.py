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

import time
import shutil
import tempfile

from PIL import Image,ImageFont,ImageDraw
from PIL.Image import Resampling

from transformers import pipeline

import random
import numpy as np
from colorthief import ColorThief

import asyncio
import telegram

import warnings
warnings.filterwarnings("ignore")


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
        
    final_summary={"Name":manga_name,"Cover Image":manga_img,"Author":manga_author,
                    "Current Status": manga_status,"Manga Genre":manga_genre,"Manga Total Views":manga_views,
                    "Rating":manga_rating,"Description":manga_desc,"chapters_info":index_info}
    return final_summary

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

def create_temp_dir(target_path):
    path = os.path.join(tempfile.mkdtemp(), str(target_path))
    if not os.path.exists(path):
        os.makedirs(path)
    return path

def create_temp_file(temp_dir_path, file_name):
    temp_file_path = os.path.join(temp_dir_path, file_name)

    # Open the file in write mode and close it immediately to create an empty file
    with open(temp_file_path, 'w'):
        pass
    
    return temp_file_path
        
def get_image(url,manga_nam,direc_name):
    
    temp_dir_path=create_temp_dir(direc_name)
    temp_file_path=create_temp_file(temp_dir_path, str(manga_name) +".jpg")

    r = requests.get(url, stream=True)
    if r.status_code == 200:
        with open(temp_file_path, 'wb+') as f:
            shutil.copyfileobj(r.raw, f)
        print("\nImage Downloaded from " + str(url) + "\n")
        return temp_dir_path
    else:
        print("\nImage can't be retrieved\n")
        return None


def dominant_color(temp_file_path):
    color_thief = ColorThief(temp_file_path)
    dominant_color = color_thief.get_color(quality=1)
    return dominant_color

def closest(colors,color):
    colors = np.array(colors)
    color = np.array(color)
    distances = np.sqrt(np.sum((colors-color)**2,axis=1))
    index_of_smallest = np.where(distances==np.amin(distances))
    smallest_distance = colors[index_of_smallest]
    return smallest_distance 

def text_contrast(r,g,b):
    threshold=0.5
    brightness=(0.299 * r + 0.587 * g + 0.114 * b) / 255 #YIQ Equation
    print(brightness)
    if brightness >= threshold:
        print("black\n")
        return "black"
    else:
        print("white\n")
        return "white"

def get_background(bg_color,page=1):
    source = requests.get(f"https://api.unsplash.com/search/photos?color={bg_color}&query=abstract-wallpaper&orientation=portrait&page={page}&per_page=30&client_id=y4x9lO2CwPOTIfeaND9bgCXbky-8PzYQrbAUiAEl-S8").json()
    return source

def get_summary(desc_text):
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn") #1.14GB
    ARTICLE =desc_text
    summarized_text=summarizer(ARTICLE, truncation=True, min_length=30, do_sample=False)
    return summarized_text

def break_fix(text, width, font, draw):
    """
    Fix line breaks in text.
    """
    if not text:
        return
    if isinstance(text, str):
        text = text.split() # this creates a list of words

    lo = 0
    hi = len(text)
    while lo < hi:
        mid = (lo + hi + 1) // 2
        t = ' '.join(text[:mid]) # this makes a string again
        bbox = draw.textbbox(xy=(0, 0), text=t, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        if w <= width:
            lo = mid
        else:
            hi = mid - 1
    t = ' '.join(text[:lo]) # this makes a string again
    bbox = draw.textbbox(xy=(0, 0), text=t, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    yield t, w, h
    yield from break_fix(text[lo:], width, font, draw)


def fit_text(img, text, color, font,crop_hieght):
    width = img.size[0]-2
    draw = ImageDraw.Draw(img)
    pieces = list(break_fix(text, width, font, draw))
    print(pieces)
    height = sum(p[2] for p in pieces) - crop_hieght
    if height > img.size[1]:
        raise ValueError("text doesn't fit")
    y = (img.size[1] - height) // 2
    for t, w, h in pieces:
        x = (img.size[0] - w) // 2
        draw.text((x, y), t, font=font, fill=color)
        y += h


def overlay_title(image,title,color):
    font = ImageFont.truetype(font='./fonts/Exo2-Regular.ttf', size=370)
    fit_text(image, title, color, font,1700)
    return image

def overlay_summary(image,summary,color):
    font = ImageFont.truetype(font='./fonts/AlegreyaSans-Medium.ttf', size=270)
    fit_text(image, summary, color, font,4900)
    return image

async def telegram_bot():
        bot = telegram.Bot(token='5645131902:AAEoxet4b1gMaL3GPCx83oKAmtPA-Ke67Fc')

        chat_id = '-846378359'

        message = f"""
        ----------------------------------------
          KASHYA'S MANGA NEWSLETTER - {datetime.date.today()}
        ----------------------------------------

        Hey fellow otakus!

        It's time for another edition of Kashya's Manga Newsletter! 

        Here are some of the titles that caught our eye.


        ----------------------------------------
                    """

        list_of_image_paths = [f for f in file_paths if f.endswith('.png')]

        await bot.send_message(chat_id=chat_id, text=message)

        for image_path in list_of_image_paths:
            try:
                file_size = os.path.getsize(image_path)
                if file_size == 0:
                    raise ValueError(f"File {image_path} is empty")
                with open(image_path, 'rb') as f:
                    for i in range(5): # Retry up to 5 times
                        try:
                            await bot.send_photo(chat_id=chat_id, photo=f)
                            break # Break out of the retry loop if the message is sent successfully
                        except telegram.error.TimedOut:
                            print("Timed out. Retrying...")
                            await asyncio.sleep(5) # Wait for 5 seconds before retrying
            except Exception as e:
                print(f"Error sending photo {image_path}: {e}")


if __name__=="__main__":

    #--------------------------------------------------
    #           SCRAPER PART
    #--------------------------------------------------

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

    #--------------------------------------------------
    #           POSTPROCESSING PART
    #--------------------------------------------------

    temp_file_path = os.path.join(final_info_file, 'final_data_file.json')


    print("\nSTARTED PREPARING DF")
    start=time.time()

    with open(temp_file_path, 'r') as temp_file:
        info = json.load(temp_file)

    df = pd.DataFrame(columns=['Name','Cover Image','Author','Current Status','Manga Genre', 'Manga Total Views','Rating','Description','Chapter_Count'])

    for url,val in info.items():
        df.loc[len(df.index)] = [info[url]['Name'], info[url]['Cover Image'], info[url]['Author'],
                                 info[url]['Current Status'],info[url]['Manga Genre'],info[url]['Manga Total Views'],
                                 info[url]['Rating'],info[url]['Description'],len(list(info[url]['chapters_info'].keys()))]

    df['Rating_Value'] = df['Rating'].apply(lambda x: x.split("/")[0])
    df['View_Count']=df['Rating'].apply(lambda x: x[x.find("-")+1:x.find("v")].replace(" ","").replace(",",""))

    df['Rating_Value']=df['Rating_Value'].replace('',0)
    df['View_Count']=df['View_Count'].replace('',0)
    df['Chapter_Count']=df['Chapter_Count'].replace('',0)

    df=df[df['Chapter_Count']>=25]

    df['Rating_Value']=df['Rating_Value'].astype(float)
    df['View_Count']=df['View_Count'].astype(int)
    df['Chapter_Count']=df['Chapter_Count'].astype(int)

    df=df.sort_values(by=['Chapter_Count','View_Count','Rating_Value'], ascending=[True, False,False],ignore_index=True).head(10)

    # Create a temporary directory with a unique name
    csv_dir = tempfile.mkdtemp(prefix='csv_storage')

    # Create a temporary file inside the directory
    csv_file_path = os.path.join(csv_dir, 'full_test.csv')

    df.to_csv(csv_file_path,index=False)

    print((time.time()-start)/60)

    print("DF PREPARTION OVER\n")

    #--------------------------------------------------
    #           FINAL POST GENERATION PART
    #--------------------------------------------------


    csv_file_path = os.path.join(csv_dir, 'full_test.csv')

    os.environ["TOKENIZERS_PARALLELISM"] = "false"

    rgb_colors={ 
    "black":[0,0,0], 
    "white":[255,255,255], 
    "yellow":[255,255,0], 
    "orange":[255,165,0], 
    "red":[255,0,0], 
    "purple":[128,0,128], 
    "magenta":[255,0,255], 
    "green":[0,128,0], 
    "teal":[0,128,128],
    "blue":[0,0,255]}

    list_of_colors=list(rgb_colors.values())



    df=pd.read_csv(csv_file_path)

    samples_dir=create_temp_dir("test_samples")

    for idx in range(len(df)):
        
        manga_name=df.iloc[idx][0]
        cover_img_url=df.iloc[idx][1]
        manga_desc=df.iloc[idx][7]
        
        print(f"\n\nSTARTED PROCESSING '{manga_name}'\n")
        print("-"*len(str(manga_name)) +"---------------------")
        print(manga_name,cover_img_url,manga_desc)
        
        manga_name=re.sub(r"[^\w\s]", "", manga_name)
        manga_name=manga_name.replace("  "," ").replace(" ","_")

        cover_path=get_image(cover_img_url,manga_name,"cover_image_samples")
        cover_file_path=os.path.join(cover_path, str(manga_name) +".jpg")

        print("Cover Image Obtained\n")
        
        
        r,g,b=dominant_color(cover_file_path)
        print("RGB values of cover image obtained\n")
        
        print("\nFinding the closest color to dominant color to be used for Unsplash API")
        color = [r,g,b]
        closest_color = closest(list_of_colors,color)
        closest_color = closest_color.tolist()[0]
        for cname,crgb in rgb_colors.items():
            if crgb == closest_color:
                print("Color found: "+str(cname))
                bg_color=str(cname)
                break
                
        print("\nFinding text's color to be used")
        text_color=text_contrast(r,g,b)
        
        print("\nGetting background from Unsplash")
        bg_image_dict=get_background(bg_color) #fetching first page
        dict_results=bg_image_dict["results"]

        single_page_dict={val["urls"]["small"] :val["likes"] for val in dict_results}

        print("\nFetching the bg with highest likes")
        sorted_bgs=sorted(single_page_dict.items(), key=lambda kv:(kv[1], kv[0]))
        bg_idx=-1*(random.randint(1,5))
        final_bg_url=sorted_bgs[bg_idx][0]
        final_bg_likes=sorted_bgs[bg_idx][1]

        fina_bg_id=final_bg_url[final_bg_url.find("-")+1:final_bg_url.find("?")]

        bg_dir_path=get_image(final_bg_url,fina_bg_id,"cover_image_samples")
        bg_path=os.path.join(bg_dir_path, str(manga_name) +".jpg")
        
        print("\nFetching final text to be printed")
        summarized_text=get_summary(manga_desc)
        print("\n")
        print(summarized_text)
        
        summary= summarized_text[0]['summary_text']

        bg = Image.open(bg_path)
        cover=Image.open(cover_file_path).convert("RGBA")

        bg=bg.resize((4433,7880),Resampling.LANCZOS)
        cover=cover.resize((3500,4000),Resampling.LANCZOS)

        image_copy = bg.copy()
        position=(550,400)
        image_copy.paste(cover, position,mask=cover)
        print("\nBackgroud image created")

        title=str(df.iloc[idx][0])
        summary = str(summary)

        print("\nOverlaying title & summary")
        image_copy=overlay_title(image_copy,title,text_color)
        image_copy=overlay_summary(image_copy,summary,text_color)

        width, height = image_copy.size
        TARGET_WIDTH = 500
        coefficient = width / 500
        new_height = height / coefficient

        image_copy = image_copy.resize((int(TARGET_WIDTH),int(new_height)),Image.LANCZOS)

        print("\nFinal image generated")

        
        samples_path=os.path.join(samples_dir, str(manga_name) +".png")
        image_copy.save(samples_path,quality=95,optimize=True)

    #--------------------------------------------------
    #           TELEGRAM TRANSMISSION PART
    #--------------------------------------------------


    file_paths = [os.path.join(samples_dir, f) for f in os.listdir(samples_dir) if os.path.isfile(os.path.join(samples_dir, f))]


    print("\nTRANSMITTING TO TELEGRAM")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(telegram_bot())
    loop.close()
    print("\nTRANSMISSION ENDED")

    shutil.rmtree(samples_dir)
    shutil.rmtree(csv_dir)
    shutil.rmtree(cover_path)
    shutil.rmtree(bg_dir_path)
    shutil.rmtree(final_info_file)




        
