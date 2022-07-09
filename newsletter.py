from colorthief import ColorThief
from bs4 import BeautifulSoup as BS
from requests import get
import os #usage to removed later by using temp files
import requests
import shutil
import random
import json
import numpy as np

from PIL import Image

from summary import get_summary
from final_image import single_manga_post

def zerochan_cover(o_manga_name):
	url="https://www.zerochan.net/" + o_manga_name
	r=get(url)
	soup=BS(r.text,"html.parser")
	
	try:
		menu_body=soup.find_all("div",{"id":"menu"})
		cover_image=menu_body[0].find("p",{"style":"text-align: center; "}).img.get('src')
		print("\nZerochan cover image found for " +str(o_manga_name) +"\n")
		return cover_image
	except:
		print("\nZerochan image unavailable")
		print("Using orignal cover image\n")
		return None
	
def dominant_color(manga):
	try:
		path="./cover_image_samples/"+str(manga)
	except Exception as e:
		print(e)
		return None
	color_thief = ColorThief(path)
	dominant_color = color_thief.get_color(quality=1)
	return dominant_color
	
def text_contrast(r,g,b):
	threshold=128
	brightness=((r * 299) + (g * 587) + (b * 114)) / 1000 #YIQ Equation
	print(brightness)
	if brightness >= threshold:
		print("black\n")
		return "black"
	else:
		print("white\n")
		return "white"

#def save_info(final_result):
#	with open("./cover_images/cover_images.json" ,"w") as output_file:
#		json.dump(final_result,output_file)

#Using Texture bg with potrait mode
def get_background(bg_color,page=1):
	source = requests.get("https://api.unsplash.com/search/photos?color={main_color}&query=cool-background&orientation=portrait&page={page_no}&per_page=30&client_id=y4x9lO2CwPOTIfeaND9bgCXbky-8PzYQrbAUiAEl-S8".format(page_no=page,main_color=bg_color)).json()
#	save_info(source)
	return source

def get_complementary(color): #hex_val_color
    color = color[1:]
    color = int(color, 16)
    comp_color = 0xFFFFFF ^ color
    comp_color = "#%06X" % comp_color
    return comp_color
 
 
#Valid values:
#black_and_white,
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
	

list_of_colors = [[0,0,0],[255,255,255],[255,255,0],[255,165,0],[255,0,0],[128,0,128],[255,0,255],[0,128,0],[0,128,128],[0,0,255]]


def closest(colors,color):
    colors = np.array(colors)
    color = np.array(color)
    distances = np.sqrt(np.sum((colors-color)**2,axis=1))
    index_of_smallest = np.where(distances==np.amin(distances))
    smallest_distance = colors[index_of_smallest]
    return smallest_distance 

def create_dir(target_path):
	path="./"
	try:
		path=path+str(target_path)
		os.mkdir(path)
	except:
		pass
		
def get_image(url,image_name,mflag=0):

	if mflag==1: #manga
		create_dir("./cover_image_samples/")
		file_name="./cover_image_samples/"+str(image_name)
	elif mflag==0: #bg
		create_dir("./bg_images/")
		file_name="./bg_images/"+str(image_name)
		
	r=requests.get(url,stream=True)
	if r.status_code==200:
		with open(file_name,'wb') as f:
			shutil.copyfileobj(r.raw,f)
		print("\nImage Downloaded from " +str(url)+"\n")
		return file_name
	else:
		print("\nImage can't be retrieved\n")
		return None
	
	
def fetch_bg_urls(dict_results):
	single_page_dict={}
	for bg_result in dict_results:
		bg_urls=bg_result["urls"]
		bg_url_regular=bg_urls["small"]
		bg_url_regular=bg_url_regular[34:60]
		if bg_url_regular[-3]=="?":
			bg_url_regular=bg_url_regular[:-3]
		likes=bg_result["likes"]
		single_page_dict.update({bg_url_regular:likes})
	return single_page_dict
		
def final_post(final_info):
	manga=final_info["Manga's name"]
	manga_cover_image=final_info["Manga's cover image"]
	manga_desc=final_info["Manga's description"]
	
	final_cover_image=zerochan_cover(manga)
	if final_cover_image==None:
		final_cover_image=manga_cover_image
	cover_path=get_image(final_cover_image,manga,mflag=1)
	if cover_path==None:
		return None
	try:
		r,g,b=dominant_color(manga)
	except Exception as e:
		print(e)
		return None
	print("\nRGB value of dominant color in manga's cover image is:")
	print(str(r)+" "+str(g)+" "+str(b)+"\n")
	
	print("\nFinding complementary color for the background")
	hex_val = "#%02x%02x%02x" % (r,g,b)
	h = get_complementary(hex_val)
	print("Complementary color",h)
	h = h.lstrip('#')
	r_c, g_c, b_c=tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
	print("RGB value of the color complementary to manga's cover image is:")
	print(str(r_c)+" "+str(g_c)+" "+str(b_c)+"\n")
	
	print("\nFinding the closest color to complementay color to be used for Unsplash API")
	color = [r_c,g_c,b_c]
	closest_color = closest(list_of_colors,color)
	closest_color = closest_color.tolist()[0]
	for cname,crgb in rgb_colors.items():
		if crgb == closest_color:
			print("Color found: "+str(cname))
			bg_color=str(cname)
			break

	print("\nFinding text's color to be used")
	text_color=text_contrast(r_c,g_c,b_c)
	
	print("\nGetting background from Unsplash")
	all_page_dict={}					   #suspended usage
	bg_image_dict=get_background(bg_color) #fetching first page
	dict_results=bg_image_dict["results"]
	
	single_page_dict=fetch_bg_urls(dict_results)
	all_page_dict.update(single_page_dict)  #suspended usage
	 
	remaining_reqs=int(bg_image_dict["total_pages"])  #suspended usage
	total=1                                           #suspended usage
	
	#----------------------------------------------------------
	#The following code snippet exceeds unsplash non production API per hour limit of <50 reqs.
	# so suspending until I get production API
	
	#for reqs in range(2,remaining_reqs): #fetching reamaining pages
	#	bg_image_dict=get_background(bg_color,page=reqs)
	#	dict_results=bg_image_dict["results"]
	#	
	#	single_page_dict=fetch_bg_urls(dict_results)
	#	all_page_dict.update(single_page_dict)
	#----------------------------------------------------------
	
		
	print("\nFetching the bg with highest likes")
	sorted_bgs=sorted(all_page_dict.items(), key=lambda kv:(kv[1], kv[0]))
	hr_image=-1*(random.randint(1,10))
	final_bg_url_id=sorted_bgs[hr_image][0]
	final_bg_likes=sorted_bgs[hr_image][1]
	
	
	final_bg_url="https://images.unsplash.com/photo-{url_id}?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=MnwzNDMxMzd8MHwxfHNlYXJjaHwxNzl8fHRleHR1cmUtYmFja2dyb3VuZHxlbnwwfDF8fHRlYWx8MTY1Njk0Mjg4Mg&ixlib=rb-1.2.1&q=80&w=1080%27:".format(url_id=final_bg_url_id)
	
	print("\nDownloading final bg url with id-{url_id} and {like_no} likes".format(url_id=final_bg_url_id,like_no=final_bg_likes))
	bg_path=get_image(final_bg_url,final_bg_url_id)
	if bg_path==None:
		return None
		
	print("\nFetching final text to be printed")
	summarized_text=get_summary(manga_desc)[0]["summary_text"]
	print("\n")
	print(summarized_text)
	
	print("\n Final post prepartion started")
	final_manga_img=single_manga_post(manga,summarized_text,cover_path,bg_path,text_color)
	
