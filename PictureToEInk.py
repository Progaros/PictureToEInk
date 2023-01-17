from PIL import Image  # pip install pillow
import os
from numpy import random  # pip install numpy


""" This script converts a picture to a black and white image for an eInk display. (only pure black and white) """
""" Place the script in the same folder as the picture(s) you want to convert. """


### SETTINGS ###
noise = 0.1    # 0-1
quality = 6    # higher = more accurate, but slower (~2-7)
### END SETTINGS ###


# check if the user has installed the required libraries
try:
    import numpy
except ImportError:
    print('Please install numpy (pip install numpy)')
    exit()
try:
    from PIL import Image
except ImportError:
    print('Please install pillow (pip install pillow)')
    exit()

# get the path (folder) of the current file
path = os.path.dirname(os.path.abspath(__file__))
# get all pictures (ignore python files and pictures containing "_eInk" in the middle)
pictureFiles = [f for f in os.listdir(
    path) if not f.endswith('.py') and not '_eInk' in f]
# if there are no files, exit
if len(pictureFiles) == 0:
    print('No files found.')
    exit()
elif len(pictureFiles) == 1:
    # if there is only one file, use it
    choice = 0
else:
    # let the user choose which file to convert
    print('Which file do you want to convert?')
    for i in range(len(pictureFiles)):
        print(str(i) + ': ' + pictureFiles[i])
    choice = int(input('Enter the number of the file: '))

# open the file
image = Image.open(pictureFiles[choice])
print('Converting ' + pictureFiles[choice] + ' to black and white...')
# get the pixels
pixels = image.load()

# get the brightness of each pixel
# loop through the pixels
for x in range(image.size[0]):
    for y in range(image.size[1]):
        # get the pixel
        pixel = pixels[x, y]
        # skip if the pixel is transparent
        if pixel[3] == 0:
            continue
        # get perceived brightness
        brightness = (pixel[0] * 0.299) + \
            (pixel[1] * 0.587) + (pixel[2] * 0.114)
        # set the pixel to the brightness
        pixels[x, y] = (int(brightness), int(brightness), int(brightness))

print('Done!')

# generate a new image
outImage = Image.new('RGBA', image.size)
outPixels = outImage.load()

print('Converting to eInk...')

# make the image eInk friendly
# loop through the pixels
for x in range(image.size[0]):
    # print progress in one line
    print('Progress:\t' +
          str(round(x / image.size[0] * 100, 1)) + '%', end='\r')

    for y in range(image.size[1]):
        # get the pixel
        pixel = pixels[x, y]
        # skip if the pixel is transparent
        if pixel[3] == 0:
            continue
        # get surrounding pixels
        surroundingPixels = []
        for i in range((0-quality), (quality+1)):
            for j in range((0-quality), (quality+1)):
                # skip if the pixel is out of bounds
                if x + i < 0 or x + i >= image.size[0] or y + j < 0 or y + j >= image.size[1]:
                    continue
                # calcualte distance to the pixel (to make the surrounding pixels more important)
                distance = (i**2 + j**2) ** 0.5
                distanceValue = 1 / (distance + 1)
                surroundingPixels.append((pixels[x+i, y+j], distanceValue))
        # get the average brightness of the surrounding pixels (weighted by distance)
        averageBrightness = sum([p[0][0] / p[1] for p in surroundingPixels]) / \
            sum([1 / p[1] for p in surroundingPixels])

        # if the pixel is brighter than the average, make it white (including some randomness)
        if (pixel[0] * random.normal(1, noise)) > averageBrightness:
            outPixels[x, y] = (255, 255, 255, 255)
            # else make it black
        else:
            outPixels[x, y] = (0, 0, 0, 255)

print('Progress: 100.0%')
print('Done!')

# save the file to "filename_eInk.png"
outputFile = pictureFiles[choice].split(
    '.')[0] + '_eInk.' + pictureFiles[choice].split('.')[1]
outImage.save(outputFile)

print('Saved as ' + outputFile)
