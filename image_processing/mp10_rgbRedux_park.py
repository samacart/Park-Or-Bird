import multiprocessing
import glob
import PIL
from PIL import Image
from PIL import ImageFilter
import numpy as np
import os
import sys
import gzip

def worker(num):

    path = '/gpfs/gpfsfpo/Park/*' + str(num) + '.jpg'
    outFile = '/gpfs/gpfsfpo/park_ml_rdx/park_rdx_' + str(num) + '.txt.gz'
    errFile = '/gpfs/gpfsfpo/errors/park_err_' + str(num) + '.txt'

    with gzip.open(outFile, 'ab') as f:
        for fn in glob.glob(path):
            #print os.path.basename(fn), str(num)
            try:
                img = Image.open(fn)
                blocks = 4
                feature = [0] * blocks * blocks * blocks
                pixel_count = 0

                for pixel in img.getdata():
                    ridx = int(pixel[0]/(256/blocks))
                    gidx = int(pixel[1]/(256/blocks))
                    bidx = int(pixel[2]/(256/blocks))
                    idx = ridx + gidx * blocks + bidx * blocks * blocks
                    feature[idx] += 1
                    pixel_count += 1

                arr = [x/float(pixel_count) for x in feature]
                output = os.path.basename(fn) + "," + ' '.join(map(str, arr)) + "\n"
                f.write(output)

            except:
                #print sys.exc_info()
                with open(errFile, 'a') as err:
                    err.write(fn + '\n')

    return

if __name__ == '__main__':
    jobs = []
    for i in range(10):
        p = multiprocessing.Process(target=worker, args=(i,))
        jobs.append(p)
        p.start()
