from pyspark.context import SparkContext
from pyspark.mllib.util import MLUtils
from pyspark.mllib.tree import RandomForest, RandomForestModel

sc = SparkContext('yarn', 'weather_predictor')

data = MLUtils.loadLibSVMFile(sc,
                              'hdfs:///users/wfvining/'+sys.argv[1])

(train, test) = data.randomSplit([0.7, 0.3])

model = RandomForest.trainRegressor(trainData,
                                    categoricalFeaturesInfo={x:2
                                                             for x
                                                             in range(654, 615)},
                                    numTrees=10, featureSubsetStrategy='auto',
                                    maxDepth=5)
predictions = model.predict(test.map(lambda x:x.features))
labelsAndPredictions = test.map(lambda lp:lp.label).zip(predictions)
testErr = labelsAndPredictions.map(
    lambda (v, p): (v - p) * (v - p)).sum() / float(test.count())
print('Mean Squared Error: ' + str(testErr)e

