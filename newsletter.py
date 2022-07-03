from colorthief import ColorThief
from bs4 import BeautifulSoup as BS
from requests import get

import requests
import shutil

import json
import numpy as np


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
	if brightness >= threshold:
		print("black\n")
	else:
		print("white\n")

def save_info(final_result):
	with open("./cover_images/cover_images.json" ,"w") as output_file:
		json.dump(final_result,output_file)

#Using Texture bg with potrait mode
def get_background(bg_color):
	source = requests.get("https://api.unsplash.com/search/photos?color={main_color}&query=texture-background&orientation=portrait&client_id=y4x9lO2CwPOTIfeaND9bgCXbky-8PzYQrbAUiAEl-S8".format(main_color=bg_color)).json()
	save_info(source)
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



def get_image(url,manga):
	file_name="./cover_image_samples/"+str(manga)
	r=requests.get(url,stream=True)
	if r.status_code==200:
		with open(file_name,'wb') as f:
			shutil.copyfileobj(r.raw,f)
		print("\nImage Downloaded from " +str(url)+"\n")
	else:
		print("\nImage can't be retrieved\n")
		
		
def final_post(manga,manga_cover_image):
	final_cover_image=zerochan_cover(manga)
	if final_cover_image==None:
		final_cover_image=manga_cover_image
	get_image(final_cover_image,manga)
	
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
	text_contrast(r_c,g_c,b_c)
	
	print("\nGetting background from Unsplash")
	bg_image_dict=get_background(bg_color)
	print(type(bg_image_dict))
	print(bg_image_dict)
	
	print("\nFetching each url")
	
		
if __name__=="__main__":
	get_background()
