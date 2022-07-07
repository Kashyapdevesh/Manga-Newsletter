from PIL import Image,ImageFont,ImageDraw
from PIL.Image import Resampling
import textwrap

from string import ascii_letters


bg = Image.open("./bg_images/1582738411706-bfc8e691d1c2")
cover=Image.open("./cover_image_samples/Death Note").convert("RGBA")

bg=bg.resize((4433,7880),Resampling.LANCZOS)
cover=cover.resize((3500,4000),Resampling.LANCZOS)

image_copy = bg.copy()
position=(450,450)
image_copy.paste(cover, position,mask=cover)


font = ImageFont.truetype(font='./SourceCodePro-Bold.ttf', size=370)

draw = ImageDraw.Draw(im=image_copy)

text = """I tried to save the sub male lead, who was poisoned by the female lead, but an accident happened! He said he would repay the favor, but he randomly sent me to the most notorious villain, the Family of Assassins?! The family that consists of the oldest brother, a knight in the Imperial Army preparing for a revolt, the second brother, a reverend with a large bounty on his head, and a father who is the greatest villain of all time… Will I be safe in this villainous family throughout my three year contract? """

# Calculate the average length of a single character of our font.
# Note: this takes into account the specific font and font size.
avg_char_width = sum(font.getsize(char)[0] for char in ascii_letters) / len(ascii_letters)

# Translate this average length into a character count
max_char_count = int(image_copy.size[0] * .618 / avg_char_width)

# Create a wrapped text object using scaled character count
text = textwrap.fill(text=text, width=max_char_count)

draw.text(xy=(image_copy.size[0]/2, image_copy.size[1]/1.68), text=text, font=font, fill='#000000', anchor='mm')

image_copy.show()
