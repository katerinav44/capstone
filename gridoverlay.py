import cv2
import matplotlib
import matplotlib.pyplot as plt
import numpy as np

"""Uses screenshot of Maverick solar farm map1.jpg to find all solar panel bays/rows.
   Returns a list of coordinates (center) of each bay/row."""

img=cv2.imread('map1.jpg') #load image

# Apply thresholding to convert grayscale to binary image
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
ret, thresh = cv2.threshold(gray, 50, 255, 1)

#apply bilateral filtering to get rid of trees and small clumps
thresh = cv2.bilateralFilter(thresh, 5, 255, 255)

#find all connected components (panels)
num_labels, labels, stats, centroids =cv2.connectedComponentsWithStats(thresh, 4, cv2.CV_32S)


# Get original imaage dimensions
height, width = img.shape[:2]

# Calculate new dimensions in m
scale_factor=483/331 #483 m /331 pixels (got this from map_scale.png image, it is 331 pixels wide and the scale says 483 m)
new_width = width * scale_factor  # In m
new_height = height * scale_factor  # In m

dpi = 96 #dots per inch of map image
#initialize figure
figsize = (width / dpi, height / dpi)  # Convert pixels to inches for figsize
fig, ax = plt.subplots(figsize=figsize)  

# Display the binary image
ax.imshow(thresh, cmap='gray', vmin=0, vmax=255)
L=[] #list to store all the panel coordinates

for i in range(num_labels):
    x = stats[i, cv2.CC_STAT_LEFT] #x coordinate of connected component
    y = stats[i, cv2.CC_STAT_TOP] #y coordinate of connected component
    w = stats[i, cv2.CC_STAT_WIDTH] #width of connected component
    h = stats[i, cv2.CC_STAT_HEIGHT] #height of connected component
    area = stats[i, cv2.CC_STAT_AREA] #area of connected component

    if area >500 and area<10000 and h>100: #filter out the connected components that have a too small height/area
        rect = matplotlib.patches.Rectangle((x, y), w, h, linewidth=1, facecolor = list(np.random.choice(range(256), size=3)/256) ) #put a rectangle of random color over each connected component (panel)
        L.append((f'{x*scale_factor:.2f}',f'{y*scale_factor:.2f}')) #append the x and y coordinates of the panel in m
        ax.add_patch(rect)



#Overlay a grid on top of the image (300 m apart)
grid_spacing = 300 #no of m apart
tick_spacing = grid_spacing / scale_factor
num_xticks = new_width / grid_spacing
num_yticks = new_height / grid_spacing

ax.set_xticks(np.arange(num_xticks)*tick_spacing,
              labels=[int(t) for t in np.arange(num_xticks) * grid_spacing], rotation=90)
ax.set_yticks(np.arange(num_yticks)*tick_spacing,
              labels=[int(t) for t in np.arange(num_yticks) * grid_spacing])
ax.grid(color='white', linewidth=1)


# Show the image
ax.axis('on')  
plt.show()
fig.savefig("map1_grid_components.jpg")

#save the list to a txt file
with open('panel_coordinates.txt', 'w') as f:
    for coord in L:
        f.write(f"{coord}\n") #newline between each tuple of coords

#Make a histogram of the connected component areas (this is useful for setting up the filter above and filtering out anything that's not a solar panel)
#Using the histogram found that <1000 -> likely tree/defect
#>10000 border of image
#h >100 panels are long rectangles
#plt.hist([a for a in stats[:,4] if a <10000], bins=50)
#plt.show()

    