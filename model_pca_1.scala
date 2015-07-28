import org.apache.spark.{SparkContext, SparkConf}
import org.apache.spark.mllib.classification.{LogisticRegressionWithSGD, LogisticRegressionWithLBFGS, LogisticRegressionModel}
import org.apache.spark.mllib.evaluation.MulticlassMetrics
import org.apache.spark.mllib.regression.LabeledPoint
import org.apache.spark.mllib.linalg.Vectors
import org.apache.spark.mllib.tree.DecisionTree
import org.apache.spark.mllib.tree.model.DecisionTreeModel
import org.apache.spark.mllib.linalg.Vector
import org.apache.spark.mllib.stat.{MultivariateStatisticalSummary, Statistics}
import org.apache.spark.mllib.feature.PCA


object model_pca_1 {

    def main(args: Array[String]) {

        val conf = new SparkConf().setAppName("Model_PCA_1")
        val sc = new SparkContext(conf)

        //val birds = sc.textFile("/gpfs/gpfsfpo/small_test/4_bird_test.txt")
        //val parks = sc.textFile("/gpfs/gpfsfpo/small_test/4_park_test.txt")

        val birds = sc.textFile("/gpfs/gpfsfpo/bird_raw_ml_2/bird_mp_0.txt.gz")
        val parks = sc.textFile("/gpfs/gpfsfpo/park_raw_ml_2")

        val b = birds.map(x => x.split(',')(1)).map(_.split(" ")).map(x=>x.map(_.toDouble)).map(x=>LabeledPoint(1,Vectors.dense(x)))
        val p = parks.map(x => x.split(',')(1)).map(_.split(" ")).map(x=>x.map(_.toDouble)).map(x=>LabeledPoint(0,Vectors.dense(x)))

        val data = b.union(p)

        val Array(training,test) = b.randomSplit(Array(0.7,0.3))

        val pca = new PCA(10).fit(training.map(_.features))

        val train_projected = training.map(p=>p.copy(features=pca.transform(p.features)))
        val test_projected = test.map(p=>p.copy(features=pca.transform(p.features)))

        val model = new LogisticRegressionWithLBFGS()
          .setNumClasses(2)
          .run(train_projected)


        // Compute raw scores on the test set.
        val predictionAndLabels = test_projected.map { case LabeledPoint(label, features) =>
          val prediction = model.predict(features)
          (prediction, label)
        }

        // Get evaluation metrics.
        val metrics = new MulticlassMetrics(predictionAndLabels)
        val precision = metrics.precision
        println("Precision = " + precision)

        val MSE = predictionAndLabels.map{case(v, p) => math.pow((v - p), 2)}.mean()
        println("Mean Squared Error = " + MSE)

        // Save model
        model.save(sc, "/gpfs/gpfsfpo/shared/model_pca_1")

    }
}
