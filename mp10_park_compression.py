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
    outFile = '/gpfs/gpfsfpo/park_ml/bird_mp_' + str(num) + '.txt.gz'
    errFile = '/gpfs/gpfsfpo/park_err_' + str(num) + '.txt'

    with gzip.open(outFile, 'ab') as f:
        for fn in glob.glob(path):
            #print os.path.basename(fn), str(num)
            try:
                img = Image.open(fn).resize((96,80), PIL.Image.ANTIALIAS)
                arr = np.array(img).flatten()
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
