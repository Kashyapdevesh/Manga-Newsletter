from PIL import Image,ImageFont,ImageDraw
from PIL.Image import Resampling


def break_fix(text, width, font, draw):
    if not text:
        return
    lo = 0
    hi = len(text)
    while lo < hi:
        mid = (lo + hi + 1) // 2
        t = text[:mid]
        w, h = draw.textsize(t, font=font)
        if w <= width:
            lo = mid
        else:
            hi = mid - 1
    t = text[:lo]
    w, h = draw.textsize(t, font=font)
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
	
def single_manga_post(manga,summary,cover_path,bg_path,color):	
	
	bg = Image.open(bg_path)
	cover=Image.open(cover_path).convert("RGBA")

	bg=bg.resize((4433,7880),Resampling.LANCZOS)
	cover=cover.resize((3500,4000),Resampling.LANCZOS)

	image_copy = bg.copy()
	position=(550,400)
	image_copy.paste(cover, position,mask=cover)
	print("\nBackgroud image created")
	
	title=str(manga)
	summary = str(summary)
	
	print("\nOverlaying title & summary")
	image_copy=overlay_title(image_copy,title,color)
	image_copy=overlay_summary(image_copy,summary,color)
	image_copy.show()
	print("\nFinal image generated")
	image_copy.save("./test_samples/{manga_name}.png".format(manga_name=manga),quality=95,optimize=True)
	return image_copy
	
if __name__=="__main__":
	img=single_manga_post("Jujutsu Kaisen","Yuuji is a genius at track and field. But he's happy as a clam in the Occult Research Club. Although he's only in the club for kicks, things get serious when a real spirit shows up.","./cover_image_samples/Jujutsu Kaisen","./bg_images/1527049979667-990f1d0d8e7f","white")


