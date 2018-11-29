**_Pre-requesites: Amazon Web Services (AWS) developer account to launch EC2 instances. AWS CLI installed in terminal and configured with credentials to talk to AWS. All steps work only in us-east-1 region_**

## AutoScaling Groups with LaunchTemplates

Below are the simple steps to run from your terminal to launch an apache-webserver on AWS EC2 by using LaunchTemplates and AutoScaling Group

1. Create launch template. (Replace securityGroupIds)
   Decode the userData and see what it has using below command in your terminal
   

     `aws ec2 create-launch-template --launch-template-data '{"ImageId":"ami-0922553b7b0369273","InstanceType":"t2.micro", "UserData": "IyEvYmluL2Jhc2gKeXVtIHVwZGF0ZSAteQphbWF6b24tbGludXgtZXh0cmFzIGluc3RhbGwgLXkgbGFtcC1tYXJpYWRiMTAuMi1waHA3LjIgcGhwNy4yCnl1bSBpbnN0YWxsIC15IGh0dHBkIG1hcmlhZGItc2VydmVyCnN5c3RlbWN0bCBzdGFydCBodHRwZApzeXN0ZW1jdGwgZW5hYmxlIGh0dHBkCnVzZXJtb2QgLWEgLUcgYXBhY2hlIGVjMi11c2VyCmNob3duIC1SIGVjMi11c2VyOmFwYWNoZSAvdmFyL3d3dwpjaG1vZCAyNzc1IC92YXIvd3d3CmZpbmQgL3Zhci93d3cgLXR5cGUgZCAtZXhlYyBjaG1vZCAyNzc1IHt9IFw7CmZpbmQgL3Zhci93d3cgLXR5cGUgZiAtZXhlYyBjaG1vZCAwNjY0IHt9IFw7CmVjaG8gIjw/cGhwIHBocGluZm8oKTsgPz4iID4gL3Zhci93d3cvaHRtbC9waHBpbmZvLnBocA==", "SecurityGroupIds": [ "sg-025def4d7af8d3d23" ], "CreditSpecification":{"CpuCredits":"standard"}}' --launch-template-name ReInvent2018LT`

2. Create an AutoScaling Group using the above LaunchTemplate and its Default version (replace subnetId)

     `aws autoscaling create-auto-scaling-group --auto-scaling-group-name ReInvent2018ASG --min-size 1 --max-size 1 --launch-template '{"LaunchTemplateName":"ReInvent2018LT", "Version": "$Default"}' --vpc-zone-identifier subnet-031cc93d`
     Note that instance launched by AutoScaling Group is t2.micro and it has a webserver running.

### Update the running AutoScaling Group by updating the Default version of LaunchTemplate

1. Create new launchtemplate version with same values as version=1, but instanceType to t2.large
     
     `aws ec2 create-launch-template-version --launch-template-data "{\"InstanceType\":\”t2.large\"}" --launch-template-name ReInvent2018LT –source-version 1`
     Note that version=2 has same values as version=1, except instanceType is modified to t2.large

2. Update Default version to 2.

     `aws ec2 modify-launch-template --launch-template-name ReInvent2018LT --default-version 2`

3. Now when above AutoScaling Group scales up, it will launch t2.large instances instead of t2.micro.


# AutoScaling Groups with LaunchTemplates and CloudFormation

## Create steps

1. Create a new CFN stack by downloading create-asg-with-lt.yaml

     `aws cloudformation create-stack --stack-name ASGWithLTAndCFN --template-body file://create-asg-with-lt.yaml`

2. Update ASG to use new instanceType 

     `aws cloudformation update-stack --stack-name ASGWithLTAndCFN --template-body file://update-asg-with-lt.yaml`

3. Changes are immediately picked up. New LaunchTemplate version is created with instanceType=t2.large. Old ASG is deleted and new one created with new LaunchTemplate version.
