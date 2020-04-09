<<<<<<< HEAD
## Sample terraform code for AWS to create Launch Templates and ASG with Mixed Instance Group
=======
# Sample Terraform Templates code  for EC2 Spot

## Contents   

The Terraform template creates the following 

**EC2 Launch Template**

**EC2 Auto Scaling Group with Mixed Instance Group with Spot and On-Demand Instance**


## Setup Commands

1. Install the terraform for your platform (Linux/Windows)
2. Install AWS CLI and configure your AWS account credentials at <YOUR_HOME_DIR>/.aws/credentials
3. git clone https://github.com/awslabs/ec2-spot-labs.git
4. cd ec2-spot-terraform
5. Replace "/home/ec2-user" with with your <YOUR_HOME_DIR> in below line in ec2-spot-terraform.tf 
   default = "/home/ec2-user/.aws/credentials"
6. terraform init
7. terraform apply


## Relevant Terraform doc links

https://www.terraform.io/docs/providers/aws/r/spot_instance_request.html

https://www.terraform.io/docs/providers/aws/r/spot_fleet_request.html

https://www.terraform.io/docs/providers/aws/r/ec2_fleet.html

https://www.terraform.io/docs/providers/aws/r/autoscaling_group.html

https://www.terraform.io/docs/providers/aws/r/autoscaling_group.html#mixed-instances-policy


## Relevant AWS doc links

https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-spotfleet.html

https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-ec2fleet.html

https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-as-group.html

https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-autoscaling-autoscalinggroup-mixedinstancespolicy.html 
>>>>>>> 9b91236a8d7d299b1ba0e68850194ed5933c9f92











