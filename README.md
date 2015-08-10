# Park or Bird? An XKCD Inspired Distributed Image Processing and Machine Learning Classifier using Spark
**Contributors: Evan Kepner, Joan Qiu, Simon Macarthur**

In computer science, it can be difficult to explain the difference between the easy and the virtually impossible. We were inspired by an <a href="http://xkcd.com/1425/" target="_blank">xkcd comic</a> to take the “park or bird” challenge using Spark and MLlib. Our goal is to build a scalable system for image processing: ingesting raw images, converting images to machine learning features, training a classifier, and ultimately building a deployable scalable prediction engine based on Spark.

#Cluster Configuration
We have configured a 3 node cluster with each node having 10 cores and 8 GB of available memory. GPFS is used as a shared filesystem for holding raw image data and Spark analysis inputs. Spark 1.4.0 is deployed across the entire cluster to minimize network traffic for source files. Due to write affinity with GPFS, we execute all transformation and data preparation scripts on the appropriate node for the stored files. Birds were stored on a single node, Parks on a single node, and Other on a single node. Spark is configured to use 6 GB of memory per executor and driver.

#Search and Data Cleansing
For our tests, we used the Flickr API to gather creative-commons licensed images and divided with user-tag searches for "park" or "birds". This included specific species and park names. Our initial tests included using the Google Search API. We did an exploration in training a classifier to predict clean data by manually labeling 2000 images. Additionally, Solr and Blacklight were deployed as a faceted search interface for the image metadata.

#Feature Extraction
We tested three variations of feature extraction for training. Our techniques create compressed files for analysis, and are configured to run in parallel on 10 CPUs per node in the cluster.
<ol>
<li>Finding the average image dimensions, rescaling to 20%, and then flattening the full RGB array. For our average image size this resulted in 20,340 features per label.
<li>Using the RGB Ratio reduction in blocks. We limited to 64 features per label with this technique.
<li>Using OpenCV and the ORB algorithm. You have different variations, but by limiting to 50 points we restrict to 1600 features.
</ol>

Features are stored in key-value pairs for ease of processing in Scala and PySpark e.g.

```
128346178290.jpg, 0 25 255 6 9 1 …. 9 82 254
```

This lets us break the key-value on the comma, and then parse the value string by spaces:

**Scala:**
```
val parks = sc.textFile("/gpfs/gpfsfpo/park_raw_ml")
val p = parks.map(x => x.split(',')(1))
	.map(_.split(" "))
	.map(x=>x.map(_.toDouble))
```

**PySpark:**
```
parks = sc.textFile("/gpfs/gpfsfpo/park_raw_ml")
p = parks.map(lambda x: x.split(',')[1])
	.map(lambda x: x.split(' '))
	.map(lambda x: [float(y) for y in x])
	.map(lambda x: Vectors.dense(x))
```

#PySpark Prediction Engine
Our trained models (without the standard scaler and PCA) can be saved to disk and used in PySpark for prediction. The prediction routine will take either a single image, or a directory of images (jpg), apply the appropriate pre-processing, and generate a predicted label.

```
# /usr/local/spark/bin/spark-submit spark-Predictor.py --help
usage: spark-Predictor.py [-h] --i I --m M

Park or Bird Prediction Engine

optional arguments:
  -h, --help         show this help message and exit
  --i I, --input I   Input file or directory of jpg images
  --m M, --method M  Model method, 1 or 2

# /usr/local/spark/bin/spark-submit spark-Predictor.py
--i /gpfs/gpfsfpo/pred_test/ --m 1

/gpfs/gpfsfpo/pred_test/8216542107.jpg
/gpfs/gpfsfpo/pred_test/503215945.jpg
/gpfs/gpfsfpo/pred_test/2792971789.jpg
/gpfs/gpfsfpo/pred_test/3655965983.jpg
/gpfs/gpfsfpo/pred_test/2792971788.jpg
/gpfs/gpfsfpo/pred_test/p_14296153.jpg
/gpfs/gpfsfpo/pred_test/8216542102.jpg
/gpfs/gpfsfpo/pred_test/5412441551.jpg
/gpfs/gpfsfpo/pred_test/p_2511878805.jpg
/gpfs/gpfsfpo/pred_test/5412441554.jpg
/gpfs/gpfsfpo/pred_test/p_534861364.jpg
/gpfs/gpfsfpo/pred_test/503215946.jpg
/gpfs/gpfsfpo/pred_test/8216542100.jpg

************* RESULTS *******************
[(u'8216542107.jpg', "IT'S A BIRD!"), (u'503215945.jpg', "IT'S A BIRD!"),
(u'2792971789.jpg', "IT'S A BIRD!"), (u'3655965983.jpg', "IT'S A BIRD!"),
(u'2792971788.jpg', "IT'S A BIRD!"), (u'p_14296153.jpg', "IT'S A BIRD!"),
(u'8216542102.jpg', "IT'S A BIRD!"), (u'5412441551.jpg', "IT'S A BIRD!"),
(u'p_2511878805.jpg', "IT'S A BIRD!"), (u'5412441554.jpg', "IT'S A BIRD!"),
(u'p_534861364.jpg', "IT'S A BIRD!"), (u'503215946.jpg', "IT'S A BIRD!"),
(u'8216542100.jpg', "IT'S A BIRD!")]
```

#Conclusions
We have demonstrated that Spark 1.4.0 can be used for image classification with logistic regression models in a scalable fashion. Our end-to-end solution provides a framework for:
<ol>
<li>Gathering image metadata in a searchable form stored in MongoDB.
<li>Collecting images based on metadata criteria and storing them in a scalable cluster.
<li>Examining and cleaning the data through a viewable portal.
<li>Index images and metadata for further investigation and faceted search.
<li>Training a machine learning model to further classify cleaned data given enough samples.
<li>Determining the average dimensions of all gathered data for potential resizing.
<li>Applying multiple image feature extraction techniques to the data based on resizing and scale invariant features such as the RGB block ratio or ORB algorithm.
<li>Applying parallelization techniques to image processing, and storing all outputs in chunked and compressed form for analysis.
<li>Training multiple machine learning models on diverse feature spaces, varying from 64 to 20,340 features across 400,000 samples.
<li>Applying standard scaler methods and principal component analysis for dimensionality reduction.
<li>Using the trained models in a deployable prediction engine built on PySpark which can take multiple model options, an input file, or an input directory, and generate classification predictions.
</ol>
