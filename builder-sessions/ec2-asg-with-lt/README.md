# AutoScaling Groups with LaunchTemplates

## Create steps

Below are the simple steps to launch an apache-webserver on AWS EC2 using ASG and LaunchTemplates

1. Create launch template (Replace securityGroupIds)

     `aws ec2 create-launch-template --launch-template-data '{"ImageId":"ami-0922553b7b0369273","InstanceType":"t2.micro", "UserData": "IyEvYmluL2Jhc2gKeXVtIHVwZGF0ZSAteQphbWF6b24tbGludXgtZXh0cmFzIGluc3RhbGwgLXkgbGFtcC1tYXJpYWRiMTAuMi1waHA3LjIgcGhwNy4yCnl1bSBpbnN0YWxsIC15IGh0dHBkIG1hcmlhZGItc2VydmVyCnN5c3RlbWN0bCBzdGFydCBodHRwZApzeXN0ZW1jdGwgZW5hYmxlIGh0dHBkCnVzZXJtb2QgLWEgLUcgYXBhY2hlIGVjMi11c2VyCmNob3duIC1SIGVjMi11c2VyOmFwYWNoZSAvdmFyL3d3dwpjaG1vZCAyNzc1IC92YXIvd3d3CmZpbmQgL3Zhci93d3cgLXR5cGUgZCAtZXhlYyBjaG1vZCAyNzc1IHt9IFw7CmZpbmQgL3Zhci93d3cgLXR5cGUgZiAtZXhlYyBjaG1vZCAwNjY0IHt9IFw7CmVjaG8gIjw/cGhwIHBocGluZm8oKTsgPz4iID4gL3Zhci93d3cvaHRtbC9waHBpbmZvLnBocA==", "SecurityGroupIds": [ "sg-025def4d7af8d3d23" ], "CreditSpecification":{"CpuCredits":"standard"}}' --launch-template-name ReInvent2018LT`

2. Create an AutoScaling Group (replace subnetId)

     `aws autoscaling create-auto-scaling-group --auto-scaling-group-name ReInvent2018ASG --min-size 1 --max-size 1 --launch-template '{"LaunchTemplateName":"ReInvent2018LT", "Version": "$Default"}' --vpc-zone-identifier subnet-031cc93d`

## Update ASG by updating LaunchTemplate

1. Create new launchtemplate version with updated values (instanceType to t2.large in this case)
     
     `aws ec2 create-launch-template-version --launch-template-data "{\"InstanceType\":\”t2.large\"}" --launch-template-name ReInvent2018LT –source-version 1`

2. Update $Default version to 2.

     `aws ec2 modify-launch-template --launch-template-name ReInvent2018LT --default-version 2`

3. Test scaling by terminating instances launched by ASG. New t2.large instances will be launched instead of t2.micro


# AutoScaling Groups with LaunchTemplates and CloudFormation

## Create steps

1. Create a new CFN stack by downloading create-asg-with-lt.yaml

     `aws cloudformation create-stack --stack-name ASGWithLTAndCFN --template-body file://create-asg-with-lt.yaml`

2. Update ASG to use new instanceType 

     `aws cloudformation update-stack --stack-name ASGWithLTAndCFN --template-body file://update-asg-with-lt.yaml`

3. Changes are immediately picked up. New LaunchTemplate version is created with instanceType=t2.large. Old ASG is deleted and new one created with new LaunchTemplate version.
