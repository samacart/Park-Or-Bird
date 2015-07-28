import org.apache.spark.{SparkContext, SparkConf}
import org.apache.spark.mllib.classification.{LogisticRegressionWithSGD, LogisticRegressionWithLBFGS, LogisticRegressionModel}
import org.apache.spark.mllib.evaluation.MulticlassMetrics
import org.apache.spark.mllib.regression.LabeledPoint
import org.apache.spark.mllib.linalg.Vectors
import org.apache.spark.mllib.tree.DecisionTree
import org.apache.spark.mllib.tree.model.DecisionTreeModel
import org.apache.spark.mllib.linalg.Vector
import org.apache.spark.mllib.stat.{MultivariateStatisticalSummary, Statistics}
object model_2 {

    def main(args: Array[String]) {

        val conf = new SparkConf().setAppName("Model_2")
        val sc = new SparkContext(conf)

        val birds = sc.textFile("/gpfs/gpfsfpo/bird_ml_rdx/train/")
        val parks = sc.textFile("/gpfs/gpfsfpo/park_ml_rdx")

        val b = birds.map(x => x.split(',')(1)).map(_.split(" ")).map(x=>x.map(_.toDouble)).map(x=>LabeledPoint(1,Vectors.dense(x)))
        val p = parks.map(x => x.split(',')(1)).map(_.split(" ")).map(x=>x.map(_.toDouble)).map(x=>LabeledPoint(0,Vectors.dense(x)))

        val data = b.union(p)

        val Array(training,test) = b.randomSplit(Array(0.7,0.3))

        //Run training algorithm to build the model
        val numIterations = 100
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
        //model.save(sc, "/gpfs/gpfsfpo/shared/model_2")
        //val sameModel = LogisticRegressionModel.load(sc, "myModelPath")

    }
}
