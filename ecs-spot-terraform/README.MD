# Create ECS cluster with Spot and On-demand capacity providers using Terraform 

Use this Terraform template to create an ECS cluster with two capacity providers connected to two Auto Scaling groups. First one with 100% EC2 Spot Instances capacity, configured with Spot best practices to get optimal capacity. Second group is 100% On-demand capacity to support workloads that are not fault tolerant.

This ECS cluster will have a default capacity providers strategy to balance tasks between on-demand and Spot instances. Which can be adjusted to fit the capacity needs for different workloads.

Capacity providers will be created with managed scaling enabled. Which will result in creating an AWS Auto Scaling plan with target tracking scaling policy. Adjust the ```target_capacity``` value in the template to control the target value for the policy metric. Check [AWS documentation](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/asg-capacity-providers-update-capacity-provider.html) for more details   


## Usage

Install Terraform -> https://learn.hashicorp.com/tutorials/terraform/install-cli

Create ECS cluster

```
cd ./ecs-spot-terraform

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
