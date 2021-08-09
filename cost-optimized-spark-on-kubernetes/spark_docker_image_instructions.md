## This document contains step-by-step instruction to build a docker image to run Spark workloads.

* Download Apache Spark from https://spark.apache.org/downloads.html 

    We are using Spark 3.0.0 here. Untar it into a folder
    ```    
    tar -xf spark-3.0.0-bin-hadoop3.2.tgz
    ```

    We are using the S3A library to read/write the data from/to Amazon S3. We need hadoop-aws JAR and aws-java-sdk-bundle JAR for that purpose. Before we build the Spark docker image lets copy them into the jars folder.
    ```
    wget https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.2.0/hadoop-aws-3.2.0.jar
    mv hadoop-aws-3.2.0.jar spark-3.0.0-bin-hadoop3.2/jars/
    wget https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.11.814/aws-java-sdk-bundle-1.11.814.jar
    mv aws-java-sdk-bundle-1.11.814.jar spark-3.0.0-bin-hadoop3.2/jars/
    ```

* Build Docker Image.
    ```
    cd spark-3.0.0-bin-hadoop3.2
    ./bin/docker-image-tool.sh -t latest -p ./kubernetes/dockerfiles/spark/bindings/python/Dockerfile build
    ```

* Push the docker image to Amazon ECR.

    Login using the cmd below don’t forget to replace the AWS_REGION and AWS_ACCOUNT_ID with your details.
    ```
    aws ecr get-login-password --region ${AWS_REGION} \
    | docker login --username AWS --password-stdin \
    ${ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com 
    ```

* Create a repository
    
    ```
    aws ecr create-repository --repository-name spark-k8-test --image-scanning-configuration scanOnPush=true --region ${AWS_REGION}
    ```

*  Tag & Push your image to Amazon ECR
    ```
    docker tag spark-py:latest ${ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/spark-k8-test:latest
    docker push ${ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/spark-k8-test:latest
    ```
