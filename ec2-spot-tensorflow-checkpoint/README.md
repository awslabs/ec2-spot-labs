## Use Tensorflow to Train and Checkpoint a Training Job
This GitHub contains sample Tensorflow code to train a simple linear model using CircleCI Amazon ECS Orb deploy which run as a container image. The code runs the training steps in a loop on a batch of data and writes checkpoints periodically to S3.
If there is an EC2 Spot interruption it restores the latest checkpoint from S3 when new Fargate Spot Instance comes up and continues training. The solution is deployed on AWS ECS Fargate Spot for low-cost, serverless task deployment.
We recommend reading this blog post for more information on this topic. The blog uses this code as sample deployment.

**What you’ll run**
A Tensorflow code to train a simple linear model. The deployment is done through CircleCI Amazon ECS Orb on AWS ECS Fargate Spot.

## Security
See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License
This library is licensed under the MIT-0 License. See the LICENSE file.
