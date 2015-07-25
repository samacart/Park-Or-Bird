import glob
from PIL import Image
import numpy as np
import os

'''
BIRD = gpfs1
PARK = gpfs2
OTHER = gpfs3
'''

def WriteImageSizes(dir_path, f):
    skip = 0
    count = 0
    for fn in glob.glob(dir_path):

        count +=1
        if count % 1000 == 0:
            print count

        try:
            img = Image.open(fn)
            f.write(str(img.size[0]) + " " + str(img.size[1]) + "\n")
        except:
            print "Skipping: {}".format(fn)
            skip += 1
            pass

    print "Skipped ratio: {}".format(skip/float(count))

if __name__ == "__main__":

    #dir_path = './test_images/*.pgm'
    dir_path = '/gpfs/gpfsfpo/Bird/*.jpg'

    f = open("/gpfs/gpfsfpo/shared/bird_size_list.txt", "wb")
    WriteImageSizes(dir_path, f)
    f.close()
