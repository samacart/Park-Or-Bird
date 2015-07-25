from pyspark.mllib.regression import LabeledPoint
from pyspark.mllib.classification import LogisticRegressionModel
from pyspark import SparkContext
import os
import glob
import PIL
from PIL import Image
import numpy as np
import sys
import gzip

def ProcessImage(f):
    img = Image.open(f).resize((96,80), PIL.Image.ANTIALIAS)
    arr = np.array(img).flatten()
    return os.path.basename(f) + ',' + ' '.join(map(str, arr))

def CreateFromFile(f, outfile):
    with gzip.open(outfile, 'ab') as pOut:
        pOut.write(ProcessImage(f))

def CreateFromDirectory(d, outfile):
    with gzip.open(outfile, 'ab') as pOut:
        for fn in glob.glob(d+'/*.jpg'):
            print fn
            try:
                pOut.write(ProcessImage(fn) + '\n')
            except:
                print "Error with: {}".format(fn)
                print sys.exc_info()
                pass

def CreateTestData(path_or_file, outfile):

    if os.path.isdir(path_or_file):
        CreateFromDirectory(path_or_file, outfile)

    else:
        CreateFromFile(path_or_file, outfile)

def main():

    outfile = '/gpfs/gpfsfpo/prediction/predict_me.txt.gz'
    os.system('rm -f ' + outfile)

    sc = SparkContext(appName="Park Bird Predction Model 1")
    CreateTestData(sys.argv[1], outfile)

    raw_input = sc.textFile(outfile)
    k = raw_input.map(lambda x: x.split(',')[0])
    p = raw_input.map(lambda x: x.split(',')[1]).map(lambda x: x.split(' ')).map(lambda x: [float(y) for y in x])

    model = LogisticRegressionModel.load(sc, '/gpfs/gpfsfpo/shared/model_1_LBFGS')
    predictions = model.predict(p)
    keyPredictions = k.zip(predictions.map(lambda x: "IT'S A BIRD!" if x==1 else "IT'S A PARK!"))

    print("************* RESULTS *******************")
    print keyPredictions.collect()

    sc.stop()

if __name__ == "__main__":
    main()
