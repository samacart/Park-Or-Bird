from pyspark.mllib.regression import LabeledPoint
from pyspark.mllib.classification import LogisticRegressionModel
from pyspark.mllib.linalg import Vectors
from pyspark import SparkContext
import os
import glob
import PIL
from PIL import Image
import numpy as np
import sys
import gzip
import argparse

def ProcessImage(f, method):

    if method == 1:
        img = Image.open(f).resize((96,80), PIL.Image.ANTIALIAS)
        arr = np.array(img).flatten()

    else:
        img = Image.open(f)
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

    return os.path.basename(f) + ',' + ' '.join(map(str, arr))

def CreateFromFile(f, method, outfile):
    with gzip.open(outfile, 'ab') as pOut:
        pOut.write(ProcessImage(f, method))

def CreateFromDirectory(d, method, outfile):

    search = d + "*.jpg" if d[-1] == "/" else d + "/*.jpg"

    with gzip.open(outfile, 'ab') as pOut:
        for fn in glob.glob(search):
            print fn
            try:
                pOut.write(ProcessImage(fn, method) + '\n')
            except:
                print "Error with: {}".format(fn)
                print sys.exc_info()
                pass

def CreateTestData(path_or_file, method, outfile):

    if os.path.isdir(path_or_file):
        CreateFromDirectory(path_or_file, method, outfile)

    else:
        CreateFromFile(path_or_file, method, outfile)

def main():

    parser = argparse.ArgumentParser(description='Park or Bird Prediction Engine')
    parser.add_argument('--i','--input', type=str, required=True, default=None, help='Input file or directory of jpg images')
    parser.add_argument('--m','--method', type=str, required=True, default=None, help='Model method, 1 or 2')
    args = parser.parse_args()

    outfile = '/gpfs/gpfsfpo/prediction/predict_me.txt.gz'
    os.system('rm -f ' + outfile)

    sc = SparkContext(appName="Park Bird Predction Model 1")

    args.m = args.m if args.m in [1,2] else 2
    model_path = '/gpfs/gpfsfpo/shared/model_1_LBFGS' if args.m == 1 else '/gpfs/gpfsfpo/shared/model_2'

    CreateTestData(args.i, args.m, outfile)

    raw_input = sc.textFile(outfile)
    k = raw_input.map(lambda x: x.split(',')[0])
    p = raw_input.map(lambda x: x.split(',')[1]).map(lambda x: x.split(' ')).map(lambda x: [float(y) for y in x]).map(lambda x: Vectors.dense(x))

    model = LogisticRegressionModel.load(sc, model_path)
    predictions = model.predict(p)
    keyPredictions = k.zip(predictions.map(lambda x: "IT'S A BIRD!" if x==1 else "IT'S A PARK!"))

    print("************* RESULTS *******************")
    print keyPredictions.collect()

    sc.stop()

if __name__ == "__main__":
    main()
