from PIL import Image
import numpy as np
import requests
import shutil

file_name='image.jpg'
url="https://avt.mkklcdnv6temp.com/33/w/25-1648354419.jpg"
r=requests.get(url,stream=True)
if r.status_code==200:
	with open(file_name,'wb') as f:
		shutil.copyfileobj(r.raw,f)
	print("\nImage Downloaded from " +str(url)+"\n")
else:
	print("\nImage can't be retrieved\n")

# Load the image
img = Image.open('image.jpg')

# Get the pixel values
pixels = np.array(img.getdata())

# Get the coordinates of the main object (e.g., using object detection)
object_coords = [(x, y) for x in range(img.width) for y in range(img.height)]

# Get the RGB values of the pixels in the main object
object_pixels = pixels[object_coords]

# Calculate the dominant color(s) of the main object
from sklearn.cluster import KMeans
kmeans = KMeans(n_clusters=3, random_state=0).fit(object_pixels)
dominant_colors = kmeans.cluster_centers_

# Convert the dominant colors from RGB to HSL or HSV
import colorsys
dominant_colors_hsv = [colorsys.rgb_to_hsv(*c) for c in dominant_colors]

# Calculate complementary, analogous, or triadic colors based on the dominant colors
from colorwheel import ColorWheel
color_wheel = ColorWheel()
color_scheme = color_wheel.triadic(dominant_colors_hsv)

# Visualize the color scheme options
import matplotlib.pyplot as plt
for color in color_scheme:
    plt.plot([0, 1], [0, 1], color=color, linewidth=3)
plt.show()

# Choose the best color scheme based on visual inspection or an objective metric
best_color = color_scheme[0]

# Apply the chosen background color to the image
background = Image.new('RGB', img.size, tuple(int(c*255) for c in best_color))
result = Image.alpha_composite(background, img)
result.save('result.jpg')
