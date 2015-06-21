from pyspark.mllib.regression import LabeledPoint
from pyspark.mllib.classification import LogisticRegressionWithSGD
from pyspark import SparkContext
import os
import pickle
import glob
from skimage import io
import numpy as np

def MakePixelFileFromImages(dir_path):

    positive_features, negative_features = [], []

    for fn in glob.glob(dir_path):
        if os.path.basename(fn).startswith('pos'):
            positive_features.append(io.imread(fn).flatten())
        else:
            negative_features.append(io.imread(fn).flatten())

    np.savetxt('pos.csv', positive_features, delimiter=",")
    np.savetxt('neg.csv', negative_features, delimiter=",")


def main():
    MakePixelFileFromImages("./CarData/TrainImages/*pgm")
    sc = SparkContext(appName="Image Classifier 01")

    p = sc.textFile("pos.csv")
    n = sc.textFile("neg.csv")

    pFeatures = p.map(lambda image: image.split(","))
    nFeatures = n.map(lambda image: image.split(","))

    pExamples = pFeatures.map(lambda features: LabeledPoint(1, features))
    nExamples = nFeatures.map(lambda features: LabeledPoint(0, features))

    data = pExamples.union(nExamples)
    (trainingData, testData) = data.randomSplit([0.7,0.3])

    trainingData.cache()

    model = LogisticRegressionWithSGD.train(trainingData)
    labels_and_predictions = testData.map(lambda image:(image.label, model.predict(image.features)))
    error_rate = labels_and_predictions.filter(lambda (val,pred): val!=pred).count() / float(testData.count())

    print("************* RESULTS *******************")
    print("Error Rate: " + str(error_rate))

    pickle.dump(model, open("imageModel.pk1","wb"))

    sc.stop()

if __name__ == "__main__":
    main()
