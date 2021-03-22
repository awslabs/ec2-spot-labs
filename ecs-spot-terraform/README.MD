# Create ECS cluster with Spot and On-demand capacity providers using Terraform

Use this Terraform template to create an ECS cluster with two capacity providers connected to two Auto Scaling groups. First one with 100% EC2 Spot Instances capacity, configured with Spot best practices to get optimal capacity. Second group is 100% On-demand capacity to support workloads that are not fault tolerant.

EC2 Spot Instances are best utilized when a wide range of mixed instance types are used across all availability zones available in the AWS region. With **capacity-optimized** allocation strategy selected in the Auto Scaling groups, the allocated capacity will be picked from the most available instance types in each availability zone.

The Auto Scaling groups will be created in the default account VPC, leveraging all available subnets. EC2 instances joining the cluster will need access to communicate with the ECS service endpoint. This template assumes that connection can be established, for more details about the possible options for connectivity check this [link](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ECS_instances.html)

This ECS cluster will have a default capacity providers strategy to balance tasks evenly between on-demand and Spot instances. Which can be adjusted to fit the capacity needs for different types of workloads, check this [link](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/cluster-capacity-providers.html) for more details about capacity providers.  

The cluster is configured to monitor Spot instances interruptions notices and set the instance in `DRAINING` status. Preventing new tasks from being scheduled for placement and moving the running ones to another instance.

Capacity providers will be created with managed scaling enabled. Which will result in creating an AWS Auto Scaling plan with target tracking scaling policy. Adjust the ```target_capacity``` value in the template to control the target value for the policy metric. Keep the value less than `100` if you want to keep a headroom for quicker scaling. For example if you set the value to `80`, this will keep additional `20%` - of the current capacity provider capacity - warmed up and ready to run tasks. Check [AWS documentation](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/asg-capacity-providers-update-capacity-provider.html) for more details

In the template you can change the EC2 instance types in each Auto Scaling group to match your tasks resources needs. Use this tool [Amazon EC2 Instance Selector](https://github.com/aws/amazon-ec2-instance-selector) to help you selecting the instance types.


## Usage

Install Terraform -> https://learn.hashicorp.com/tutorials/terraform/install-cli

Create ECS cluster

```
cd ./ecs-spot-terraform

terraform init
terraform plan
...
terraform apply
```

Delete ECS cluster
```
terraform destroy
```

## Requirements

| Name | Version |
|------|---------|
| terraform | >= 0.12.21 |
| aws | >= 2.70 |

## Modules

No Modules.
