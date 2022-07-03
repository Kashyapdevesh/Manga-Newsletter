from colorthief import ColorThief
from bs4 import BeautifulSoup as BS
from requests import get

import requests
import shutil

def zchan_cover(o_manga_name):
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
	path="./cover_image_samples/"+str(manga)
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
	cover_image=zchan_cover(manga)
	if cover_image==None:
		cover_image=manga_cover_image
	get_image(cover_image,manga)
	r,g,b=dominant_color(manga)
	text_contrast(r,g,b)
	
