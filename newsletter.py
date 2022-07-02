from colorthief import ColorThief
from bs4 import BeautifulSoup as BS
from requests import get

#CHECKING COVER AT ZEROCHAN
def zchan_cover(o_manga_name):
	url="https://www.zerochan.net/" + o_manga_name
	r=get(url)
	soup=BS(r.text,"html.parser")
	
	try:
		menu_body=soup.find_all("div",{"id":"menu"})
		cover_image=menu_body[0].find("p",{"style":"text-align: center; "}).img.get('src')
		print("Zerochan cover image found for" +str(o_manga_name))
		return cover_image
	except:
		print("Zerochan image unavailable")
		print("Using orignal cover image")
		return None
	
def dominant_color(path):
	color_thief = ColorThief(path)
	dominant_color = color_thief.get_color(quality=1)
	return dominant_color
	

