```
 # Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
 #
 # Permission is hereby granted, free of charge, to any person obtaining a copy of this
 # software and associated documentation files (the "Software"), to deal in the Software
 # without restriction, including without limitation the rights to use, copy, modify,
 # merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
 # permit persons to whom the Software is furnished to do so.
 #
 # THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
 # INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
 # PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
 # HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
 # OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
 # SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
---

bin/spark-submit \
--master k8s://<<MASTER URL>> \
--deploy-mode cluster \
--name 'Job Name' \
--conf spark.eventLog.dir=s3a://<<S3 BUCKET>>/logs \
--conf spark.eventLog.enabled=true \
--conf spark.history.fs.inProgressOptimization.enabled=true \
--conf spark.history.fs.update.interval=5s \
--conf spark.kubernetes.container.image=<<ECR Spark Docker Image>> \
--conf spark.kubernetes.container.image.pullPolicy=IfNotPresent \
--conf spark.kubernetes.driver.podTemplateFile='../driver_pod_template.yml' \
--conf spark.kubernetes.executor.podTemplateFile='../executor_pod_template.yml' \
--conf spark.kubernetes.authenticate.driver.serviceAccountName=spark \
--conf spark.dynamicAllocation.enabled=true \
--conf spark.dynamicAllocation.shuffleTracking.enabled=true \
--conf spark.dynamicAllocation.maxExecutors=100 \
--conf spark.dynamicAllocation.executorAllocationRatio=0.33 \
--conf spark.dynamicAllocation.sustainedSchedulerBacklogTimeout=30 \
--conf spark.dynamicAllocation.executorIdleTimeout=60s \
--conf spark.driver.memory=8g \
--conf spark.kubernetes.driver.request.cores=2 \
--conf spark.kubernetes.driver.limit.cores=4 \
--conf spark.executor.memory=8g \
--conf spark.kubernetes.executor.request.cores=2 \
--conf spark.kubernetes.executor.limit.cores=4 \
--conf spark.hadoop.fs.s3a.impl=org.apache.hadoop.fs.s3a.S3AFileSystem \
--conf spark.hadoop.fs.s3a.connection.ssl.enabled=false \
--conf spark.hadoop.fs.s3a.fast.upload=true \
s3a://<<S3 BUCKET>>/script.py \
s3a://<<S3 BUCKET>>/output
```