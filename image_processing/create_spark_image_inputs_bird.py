import glob
import PIL
from PIL import Image
from PIL import ImageFilter
import numpy as np
import os
import sys

'''
BIRD = gpfs1
PARK = gpfs2
OTHER = gpfs3
'''

def writeOutput(outFile, img):

    #write the image as a flattened numpy array to text files for Spark consumption
    arr = np.array(img).flatten()
    output = ' '.join(map(str, arr))
    with open(outFile, 'a') as f:
        f.write(output + "\n")

if __name__ == "__main__":

    path = '/gpfs/gpfsfpo/Bird/*.jpg'

    for fn in glob.glob(path):
        try:
            #get raw image and resize with aspect ratio
            #average size determined by prior code analysis
            raw_img = Image.open(fn).resize((478,398), PIL.Image.ANTIALIAS)

            #convert to gray scale
            gs_img = raw_img.convert("L")

            #apply Gaussian blur to the images
            raw_blur = raw_img.filter(ImageFilter.GaussianBlur(radius=2))
            gs_blur = gs_img.filter(ImageFilter.GaussianBlur(radius=2))

            #create output files for all variations
            writeOutput('/gpfs/gpfsfpo/shared/bird_raw.txt', raw_img)
            writeOutput('/gpfs/gpfsfpo/shared/bird_gs.txt', gs_img)
            writeOutput('/gpfs/gpfsfpo/shared/bird_raw_blur.txt', raw_blur)
            writeOutput('/gpfs/gpfsfpo/shared/bird_gs_blur.txt', gs_blur)

        except:
            with open('/gpfs/gpfsfpo/shared/bird_errors.log','a') as err:
                err.write(fn + "\n")
