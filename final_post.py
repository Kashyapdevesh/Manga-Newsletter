from PIL import Image,ImageFont,ImageDraw
from PIL.Image import Resampling

from transformers import pipeline

import random
import os
import requests
import shutil
import re
import numpy as np
import pandas as pd
from colorthief import ColorThief

import warnings
warnings.filterwarnings("ignore")

import sys
import tempfile
# import subprocess

csv_dir=os.environ['CSV_DIR']

# csv_dir = sys.argv[1]
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


# subprocess.call(['python', 'telegram_bot.py', samples_dir])

shutil.rmtree(csv_dir)
shutil.rmtree(cover_path)
shutil.rmtree(bg_dir_path)

os.environ['SAMPLES_DIR'] = samples_path
    