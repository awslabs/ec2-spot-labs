# Powering your Amazon ECS Cluster with Amazon EC2 Spot Instances

Example AWS CloudFormation template for running an Amazon ECS cluster on Amazon EC2 Spot Instances. Please see this [blog](https://aws.amazon.com/blogs/compute/powering-your-amazon-ecs-cluster-with-amazon-ec2-spot-instances/) post for more info.

![https://aws.amazon.com/ec2/spot/](https://img.shields.io/badge/Amazon-EC2%20Spot%20Instances-orange.svg) ![https://aws.amazon.com/asl/](https://img.shields.io/badge/License-Amazon_Software_License-orange.svg)


## Getting Started

This CloudFormation template will deploy an ECS cluster running on EC2 Spot Instances. It uses EC2 Spot Fleet to manage the Spot Instances, and includes an EC2 Spot Instance termination notice handler script to automatically set the ECS container instances in **DRAINING** state when a Spot Instance termination notice is detected. The handler script also publishes a message to an SNS topic created by the CloudFormation stack.

### Architecture

![](https://d2908q01vomqb2.cloudfront.net/1b6453892473a467d07372d45eb05abc2031647a/2017/06/05/0606-Spot-5.jpg)

### Prerequisites

Before you can use AWS CloudFormation or any Amazon Web Services, you must first sign up for an AWS account.

To sign up for an AWS account, open [https://aws.amazon.com/](https://aws.amazon.com/), and then choose **Create an AWS Account**.

Follow the online instructions.

### Pricing

AWS CloudFormation is a free service; however, you are charged for the AWS resources you include in your stacks at the current rates for each. For more information about AWS pricing, go to the detail page for each product on [http://aws.amazon.com](http://aws.amazon.com).

## Deployment

After signing up for an AWS account, you can use AWS CloudFormation through the AWS Management Console, AWS CloudFormation API, or AWS CLI.

Use the [template](ecs-ec2-spot-fleet.yaml) to create a CloudFormation stack, providing details and parameters such as the **ECS cluster target capacity**, the **instance type**, and the **Spot bid price**.

You can learn more about working with CloudFormation stacks [here](http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/stacks.html).

## AWS services used

* [AWS CloudFormation](https://aws.amazon.com/cloudformation/)
* [Amazon EC2 Container Service (ECS)](https://aws.amazon.com/ecs/)
* [Amazon EC2 Spot Instances](https://aws.amazon.com/ec2/spot/)
* [Amazon CloudWatch](https://aws.amazon.com/cloudwatch/)
* [Amazon Simple Notification Service (SNS)](https://aws.amazon.com/sns/)

## Contributing

Comments, feedback, and pull requests are always welcome.

## Authors

* [**Shawn O'Connor**](https://github.com/oak2278)
* [**Chad Schmutzer**](https://github.com/schmutze)

## License

This project is licensed under the [Amazon Software License](https://aws.amazon.com/asl/) - see the [LICENSE.txt](LICENSE.txt) file for details.
