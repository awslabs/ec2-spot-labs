# ec2-spot-sagemaker-training

This is an example notebook based off of the [SageMaker DeepAR Synthentic Example](https://github.com/awslabs/amazon-sagemaker-examples/tree/master/introduction_to_amazon_algorithms/deepar_synthetic), extended to leverage EC2 Spot Instances for training. The SageMaker documentation contains details to learn more about [Managed Spot Training with Sagemaker](https://docs.aws.amazon.com/sagemaker/latest/dg/model-managed-spot-training.html).

This example leverages the SageMaker Python SDK [](https://github.com/aws/sagemaker-python-sdk) and a high level SageMaker Estimator Interface to complete training and deployment tasks.

## Usage

1. Launch a SageMaker Notebook Instance and clone this repo into your environment.
2. Open the notebook.ipynb Notebook and complete each step to demonstrate leveraging EC2 Spot Instances for training a model.
3. The following code builds the Estimator object and configures the training job to leverage EC2 Spot Instances.
4. Checkpointing is configured so that training progress is not lost in the event of an instance interruption.

```
estimator = sagemaker.estimator.Estimator(
    sagemaker_session=sagemaker_session,
    image_name=IMAGE_NAME_GOES_HERE,
    role=ROLE_ARN_GOES_HERE,
    train_instance_count=1,                         # Configure Based On Needs
    train_instance_type='ml.c4.xlarge',             # Configure Based on Needs
    train_use_spot_instances=True,                  # Set to True to use EC2 Spot Instances
    train_max_wait=3600,                            # Max Time to Wait for EC2 Spot Instances
    train_max_run=3600,                             # Max Time to Run Training Job
    base_job_name='JOB_NAME_HOES_HERE',
    checkpoint_s3_uri='CHECKPOINT_PATH_GOES_HERE',
    output_path='S3_OUTPUT_PATH_GOES_HERE'
)
```

4. Once the training job completes, the output will contain information about billable instance hours, and the cost savings achieved with EC2 Spot Instances.

```
2019-08-26 18:33:19 Completed - Training job completed
Training seconds: 115
Billable seconds: 38
Managed Spot Training savings: 67.0%
```