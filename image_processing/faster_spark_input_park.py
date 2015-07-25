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
if __name__ == "__main__":

    path = '/gpfs/gpfsfpo/Park/*.jpg'

    with open('/gpfs/gpfsfpo/shared/park_raw.txt', 'a') as f:

        for fn in glob.glob(path):
            try:
                #get raw image and resize with aspect ratio
                #average size determined by prior code analysis

                img = Image.open(fn).resize((478,398), PIL.Image.ANTIALIAS)
                arr = np.array(img).flatten()
                output = ' '.join(map(str, arr))
                f.write(output + "\n")

            except:
                with open('/gpfs/gpfsfpo/shared/park_errors.log','a') as err:
                    err.write(fn + "\n")
