
from pyspark import SparkContext, SparkConf
conf = SparkConf().setAppName("WordCount")
sc = SparkContext(conf=conf)

file = sc.textFile("s3://commoncrawl/crawl-data/CC-MAIN-2017-22/segments/1495463607325.40/wet/")
counts = file.flatMap(lambda line: line.split(" ")).map(lambda word: (word, 1)).reduceByKey(lambda a, b: a + b)
counts.saveAsTextFile("s3://schmutze-cloud-academy/output/")