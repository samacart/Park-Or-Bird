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

    if num%2 ==0:
        prefix = 'even'
        path = '/gpfs/gpfsfpo/sample_bird/*[0,2,4,6,8].jpg'
        outFile = '/gpfs/gpfsfpo/shared/bird_mp_e.txt.gz'
        errFile = '/gpfs/gpfsfpo/shared/bird_err_e.txt'

    else:
        prefix = 'odd'
        path = '/gpfs/gpfsfpo/sample_bird/*[1,3,5,7,9].jpg'
        outFile = '/gpfs/gpfsfpo/shared/bird_mp_o.txt.gz'
        errFile = '/gpfs/gpfsfpo/shared/bird_err_o.txt'

    with gzip.open(outFile, 'ab') as f:
        for fn in glob.glob(path):
            print fn, prefix
            try:
                img = Image.open(fn).resize((478,398), PIL.Image.ANTIALIAS)
                arr = np.array(img).flatten()
                output = ' '.join(map(str, arr)) + "\n"
                f.write(output)
            except:
                print sys.exc_info()
                with open(errFile, 'a') as err:
                    err.write(fn + '\n')

    return

if __name__ == '__main__':
    jobs = []
    for i in range(2):
        p = multiprocessing.Process(target=worker, args=(i,))
        jobs.append(p)
        p.start()
