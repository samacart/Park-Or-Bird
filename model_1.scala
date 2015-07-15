import org.apache.spark.{SparkContext, SparkConf}
import org.apache.spark.mllib.classification.{LogisticRegressionWithSGD, LogisticRegressionWithLBFGS, LogisticRegressionModel}
import org.apache.spark.mllib.evaluation.MulticlassMetrics
import org.apache.spark.mllib.regression.LabeledPoint
import org.apache.spark.mllib.linalg.Vectors

object model_1 {

    def main(args: Array[String]) {

        val conf = new SparkConf().setAppName("Model_1")
        val sc = new SparkContext(conf)

        //val birds = sc.textFile("/gpfs/gpfsfpo/small_test/4_bird_test.txt")
        //val parks = sc.textFile("/gpfs/gpfsfpo/small_test/4_park_test.txt")

        val birds = sc.textFile("/gpfs/gpfsfpo/bird_raw_ml/bird_mp_0.txt.gz")
        val parks = sc.textFile("/gpfs/gpfsfpo/park_raw_ml")

        val b = birds.map(x => x.split(',')(1)).map(_.split(" ")).map(x=>x.map(_.toDouble)).map(x=>LabeledPoint(1,Vectors.dense(x)))
        val p = parks.map(x => x.split(',')(1)).map(_.split(" ")).map(x=>x.map(_.toDouble)).map(x=>LabeledPoint(0,Vectors.dense(x)))

        val data = b.union(p)
        val Array(training,test) = data.randomSplit(Array(0.7,0.3))

        training.cache()
        test.cache()

        // Run training algorithm to build the model
        val numIterations = 1
        val model = LogisticRegressionWithSGD.train(training, numIterations)

        /*
        val model = new LogisticRegressionWithLBFGS()
          .setNumClasses(2)
          .run(training)
        */

        // Compute raw scores on the test set.
        val predictionAndLabels = test.map { case LabeledPoint(label, features) =>
          val prediction = model.predict(features)
          (prediction, label)
        }

        // Get evaluation metrics.
        val metrics = new MulticlassMetrics(predictionAndLabels)
        val precision = metrics.precision
        println("Precision = " + precision)

        // Save model
        //model.save(sc, "/gpfs/gpfsfpo/shared/model_1")
        //val sameModel = LogisticRegressionModel.load(sc, "myModelPath")
    }
}


/*****
name := "Model_1"
version := "1.0"

libraryDependencies += "org.apache.spark" %% "spark-core" % "1.4.0" % "provided"
libraryDependencies += "org.apache.spark" %% "spark-streaming" % "1.4.0" % "provided"
libraryDependencies += "org.apache.spark" %% "spark-mllib" % "1.4.0"

resolvers += "Akka Repository" at "http://repo.akka.io/releases/"
******/
