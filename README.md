# Park-or-bird
In computer science, it can be difficult to explain the difference between the easy and the virtually impossible. We were inspired by an <a href="http://xkcd.com/1425/">xkcd comic</a> to take the “park or bird” challenge using Spark and MLlib. Our goal is to build a scalable system for image processing: ingesting raw images, converting images to machine learning features, training a classifier, and ultimately building a deployable scalable prediction engine based on Spark.

![Alt text](http://imgs.xkcd.com/comics/tasks.png "XKCD inspiration")

#Cluster Configuration
We have configured a 3 node cluster with each node having 10 cores and 8 GB of available memory. GPFS is used as a shared filesystem for holding raw image data and Spark analysis inputs. Spark 1.4.0 is deployed across the entire cluster to minimize network traffic for source files. Due to write affinity with GPFS, we execute all transformation and data preparation scripts on the appropriate node for the stored files. Birds were stored on a single node, Parks on a single node, and Other on a single node. Spark is configured to use 6 GB of memory per executor and driver.

#Feature Extraction
We tested three variations of feature extraction for training:
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

Scala:
```
val parks = sc.textFile("/gpfs/gpfsfpo/park_raw_ml")
val p = parks.map(x => x.split(',')(1))
	.map(_.split(" "))
	.map(x=>x.map(_.toDouble))
```

PySpark:
```
parks = sc.textFile("/gpfs/gpfsfpo/park_raw_ml")
p = parks.map(lambda x: x.split(',')[1])
	.map(lambda x: x.split(' '))
	.map(lambda x: [float(y) for y in x])
	.map(lambda x: Vectors.dense(x))
```
