import sys
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName('Amazon reviews word count').getOrCreate()
df = spark.read.parquet("s3://amazon-reviews-pds/parquet/")
df.selectExpr("explode(split(lower(review_body), ' ')) as words").groupBy("words").count().write.mode("overwrite").parquet(sys.argv[1])
exit()