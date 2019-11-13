# ec2-spot-sagemaker-training

This repository contains sample notebooks that are configured to utilize Amazon SageMaker Managed Spot Training. By leveraging Managed Spot Training for SageMaker we can use EC2 Spot Instances for our training jobs, and take advantage of significant savings

* sagemaker-deepar.ipynb - Uses the Amazon SageMaker Python SDK and the high-level Estimator abstraction for configuring and executing training jobs to train and deploy a DeepAR model. This example demonstrates single instance training with checkpointing.

* sagemaker-xgboost.ipynb - Uses the boto3 Python SDK to configure and execute training jobs to configure and deploy an XGBoost model. This example demonstrates single instance and distributed training with checkpointing.

## Usage

1. Launch a SageMaker Notebook Instance and clone this repo into your environment.
2. Open the notebook.ipynb Notebook and complete each step to demonstrate leveraging EC2 Spot Instances for training a model.
