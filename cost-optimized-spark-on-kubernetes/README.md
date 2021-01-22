## Running Cost Optimized Spark workloads on Kubernetes using EC2 Spot Instances and Amazon Elastic Kubernetes Service
This GitHub contains sample configuration files for running Apache Spark on Kubernetes using Amazon Elastic Kubernetes Service (Amazon EKS) and Amazon EC2 Spot Instances. We recommend reading this blog post for more information on this topic. The blog also contains the detailed tutorial for the step-by-step instructions below. 

**What you’ll run**

A word-count Spark application counting the words from an [Amazon Customer Review dataset](https://s3.amazonaws.com/amazon-reviews-pds/readme.html) and write the output to an Amazon S3 folder.

## Step-by-step Instructions

* Create a S3 Bucket 

* Create Amazon S3 Access Policy
    ```
    aws iam create-policy --policy-name spark-s3-policy --policy-document file://spark-s3.json
    ```
    Replace the output folder with the bucket name

* Create an EKS cluster using the following command
    ```
    eksctl create cluster –name=sparkonk8 --node-private-networking  --without-nodegroup --asg-access –region=<AWS Region>
    ```
* Create the nodegroup using the nodeGroup config file. Replace the <Policy ARN> string using the ARN string from the previous step. 
    ```
    eksctl create nodegroup -f managedNodeGroups.yml
    ```
* Create a service account
    ```
    kubectl create serviceaccount spark
    kubectl create clusterrolebinding spark-role --clusterrole='edit'  --serviceaccount=default:spark
    --namespace=default
    ```
* Download and install the Cluster Autoscaler
    ```
    curl -LO https://raw.githubusercontent.com/kubernetes/autoscaler/master/cluster-autoscaler/cloudprovider/aws/examples/cluster-autoscaler-autodiscover.yaml
    ```
    Edit it to add the cluster-name.

    Install the Cluster Autoscaler
    ```
    kubectl apply -f cluster-autoscaler-autodiscover.yaml
    ```
* Get the details of Kubernetes master url
    ```
    kubectl cluster-info
    ```
* Build the docker image using the instructions [here](spark_docker_image_instructions.md)

* Use the application file(script.py) and upload into the Amazon S3 bucket created.

* Download the pod template files

  This enables scheduling of the driver pods to On-Demand Instances and executor pods to Spot Instances  

* Submit the spark job using the command [here](spark-submit-command.md)

## Cleanup

* Delete the EKS cluster and the nodegroups with the following command:
    ```
    eksctl delete cluster --name sparkonk8
    ```
* Delete the Amazon S3 Access Policy with the following command: 
    ```
    aws iam delete-policy --policy-arn <POLICY ARN>
    ```
*   Delete the Amazon S3 Output Bucket with the following command:  
    ```
    aws s3 rb --force s3://<S3_BUCKET>
    ```
## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.

