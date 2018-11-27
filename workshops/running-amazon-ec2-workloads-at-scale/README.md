# Running Amazon EC2 Workloads at Scale: Workshop guide
  
  
## Overview
This workshop is designed to get you familiar with the concepts and best practices for requesting Amazon EC2 capacity at scale in a cost optimized architecture.

## Setting

You've been tasked with deploying a next-generation music streaming service. You do extensive research, and determine that [Koel](https://koel.phanan.net/)- a personal music streaming server (*that works)- is the perfect fit.

Requirements include the ability to automatically deploy and scale the service for both predictable and dynamic traffic patterns, all without breaking the budget.

In order to optimize performance and cost, you will use Amazon EC2 Auto Scaling to [scale across multiple instance types and purchase options](https://aws.amazon.com/blogs/aws/new-ec2-auto-scaling-groups-with-multiple-instance-types-purchase-options/).

## Requirements, notes, and legal
1. To complete this workshop, have access to an AWS account with administrative permissions. An IAM user with administrator access (**arn:aws:iam::aws:policy/AdministratorAccess**) will do nicely.

1. __This workshop is self-paced__. The instructions will primarily be given using the [AWS Command Line Interface (CLI)](https://aws.amazon.com/cli) - this way the guide will not become outdated as changes or updates are made to the AWS Management Console. However, most steps in the workshop can be done in the AWS Management Console directly. Feel free to use whatever is comfortable for you.

1. While the workshop provides step by step instructions, please do take a moment to look around and understand what is happening at each step. The workshop is meant as a getting started guide, but you will learn the most by digesting each of the steps and thinking about how they would apply in your own environment. You might even consider experimenting with the steps to challenge yourself.

1. This workshop has been designed to run in any public AWS Region that supports AWS Cloud9. See [Regional Products and Services](https://aws.amazon.com/about-aws/global-infrastructure/regional-product-services/) for details.

	>**Note: If you are attending an event, please run in the region suggested by the facilitators of the workshop.**

1. Make sure you have a valid Amazon EC2 key pair and record the key pair name in the region you are operating in before you begin. To see your key pairs, open the Amazon EC2 console, then click Key Pairs in the navigation pane.
	
	>Note: If you don't have an Amazon EC2 key pair, you must create the key pair in the same region where you are creating the stack. For information about creating a key pair, see [Getting an SSH Key Pair](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-key-pairs.html#having-ec2-create-your-key-pair) in the Amazon EC2 User Guide for Linux Instances. 

1. During this workshop, you will install software (and dependencies) on the Amazon EC2 instances launched in your account. The software packages and/or sources you will install will be from the [Amazon Linux 2](https://aws.amazon.com/amazon-linux-2/) distribution as well as from third party repositories and sites. Please review and decide your comfort with installing these before continuing.


## Architecture

In this workshop, you will deploy the following:

* An AWS CloudFormation stack, which will include:
	* An Amazon Virtual Private Cloud (Amazon VPC) with subnets in two Availability Zones
	* An AWS Cloud9 environment
	* Supporting IAM policies and roles
	* Supporting security groups
	* An Amazon EFS file system
	* An Amazon S3 bucket to use with AWS CodeDeploy
* An Amazon EC2 launch template
* An Amazon RDS database instance
* An Application Load Balancer (ALB) with a listener and target group
* An Amazon EC2 Auto Scaling group, with:
	* A scheduled scaling action
	* A dynamic scaling policy
* An AWS Systems Manager run command to emulate load on the service

Here is a diagram of the resulting architecture:

![](architecture.jpg)

## Let's Begin!  

### 1\. Launch the CloudFormation stack

To save time on the initial setup, a CloudFormation template will be used to create the Amazon VPC with subnets in two Availability Zones, as well as various supporting resources including IAM policies and roles, security groups, an S3 bucket, an EFS file system, and a Cloud9 IDE environment for you to run the steps for the workshop in.

#### To create the stack

1. You can view and download the CloudFormation temlate from GitHub [here](https://raw.githubusercontent.com/awslabs/ec2-spot-labs/master/workshops/running-amazon-ec2-workloads-at-scale/running-amazon-ec2-workloads-at-scale.yaml).

1. Take a moment to review the CloudFormation template so you understand the resources it will be creating.

1. Browse to the [AWS CloudFormation console](https://console.aws.amazon.com/cloudformation).

	>Note: Make sure you are in AWS Region designated by the facilitators of the workshop!

1. Click **Create stack**.

1. In the **Specify template** section, select **Upload a template file**. Click **Choose file** and, select the template you downloaded in step 1.

1. Click **Next**.

1. In the **Specify stack details** section, enter a **Stack name**. For example, use *runningAmazonEC2WorkloadsAtScale*. The stack name cannot contain spaces.

1. [Optional] In the **Parameters** section, optionally change the **sourceCidr** to restrict instance ssh/http access and load balancer http access.

1. Click **Next**.

1. In **Configure stack options**, you don't need to make any changes.

1. Click **Next**.

1. Review the information for the stack. At the bottom under **Capabilities**, select **I acknowledge that AWS CloudFormation might create IAM resources**. When you're satisfied with the settings, click **Create stack**.

#### Monitor the progress of stack creation

It will take roughly 5 minutes for the stack creation to complete.

1. On the [AWS CloudFormation console](https://console.aws.amazon.com/cloudformation), select the stack in the list.

1. In the stack details pane, click the **Events** tab. You can click the refresh button to update the events in the stack creation.
 
The **Events** tab displays each major step in the creation of the stack sorted by the time of each event, with latest events on top.

The **CREATE\_IN\_PROGRESS** event is logged when AWS CloudFormation reports that it has begun to create the resource. The **CREATE_COMPLETE** event is logged when the resource is successfully created.

When AWS CloudFormation has successfully created the stack, you will see the following event at the top of the Events tab:

	17 Nov 2018 06:17:21	runningAmazonEC2WorkloadsAtScale	CREATE_COMPLETE
	
#### Use your stack resources

In this workshop, you'll need to reference the resources created by the CloudFormation stack.

1. On the [AWS CloudFormation console](https://console.aws.amazon.com/cloudformation), select the stack in the list.

1. In the stack details pane, click the **Outputs** tab.

It is recommended that you keep this window open so you can easily refer to the outputs and resources throughout the workshop.

### 2\. Get familiar with the AWS Cloud9 environment

AWS Cloud9 comes with a terminal that includes sudo privileges to the managed Amazon EC2 instance that is hosting your development environment and a preauthenticated AWS Command Line Interface. This makes it easy for you to quickly run commands and directly access AWS services.

An AWS Cloud9 environment was launched as a part of the CloudFormation stack (you may have noticed a second CloudFormation stack created by Cloud9). You'll be using this Cloud9 environment to execute the steps in the workshop.

1. Find the name of the AWS Cloud9 environment by checking the value of **cloud9Environment** in the CloudFormation stack outputs.

1. Sign in to the [AWS Cloud9 console](https://console.aws.amazon.com/cloud9/).

1. Find the Cloud9 environment in **Your environments**, and click **Open IDE**.

1. Take a moment to get familiar with the Cloud9 environment. You can even take a quick tour of Cloud9 [here](https://docs.aws.amazon.com/cloud9/latest/user-guide/tutorial.html#tutorial-tour-ide) if you'd like.

### 3\. Update the AWS CLI and install dependencies

1. Make sure the latest version of the AWS CLI is installed by running:

	```
	sudo pip install -U awscli
	```
	
1. Install dependencies for use in the workshop by running:

	```
	sudo yum -y install jq amazon-efs-utils
	```

### 4\. Clone the workshop GitHub repo

In order to execute the steps in the workshop, you'll need to clone the workshop GitHub repo.

1. In the Cloud9 IDE terminal, run the following command:

	```
	git clone https://github.com/awslabs/ec2-spot-labs.git
	```
	
1. Change into the workshop directory:

	```
	cd ec2-spot-labs/workshops/running-amazon-ec2-workloads-at-scale
	```

1. Feel free to browse around. You can also browse the directory structure in the **Environment** tab on the left, and even edit files directly there by double clicking on them.

### 5\. Create an EC2 launch template

EC2 Launch Templates reduce the number of steps required to create an instance by capturing all launch parameters within one resource. 

You can create a launch template that contains the configuration information to launch an instance. Launch templates enable you to store launch parameters so that you do not have to specify them every time you launch an instance. For example, a launch template can contain the AMI ID, instance type, and network settings that you typically use to launch instances. When you launch an instance using the Amazon EC2 console, an AWS SDK, or a command line tool, you can specify the launch template to use.

You'll use a launch template to specify configuration parameters for launching instances in this workshop.

1. Edit the file **user-data.txt**. Review how it will install dependency packages, run commands to install and configure the CodeDeploy agent, and run commands to configure and mount the EFS file system.

1. Update **%awsRegionId%** with the value from the CloudFormation stack outputs.

1. Update **%fileSystem%** with the value from the CloudFormation stack outputs.

1. Save the file.

1. Convert the file to base64 for use in the launch template:

	```
	base64 --wrap=0 user-data.txt > user-data.base64.txt
	```
	
1. Next, edit **launch-template-data.json**.

1. Update the following values from the CloudFormation stack outputs: **%instanceProfile%** and **%instanceSecurityGroup%**.

1. Update **%ami-id%** with the AMI ID for the latest version of Amazon Linux 2 in the AWS region you launched. You can find the AMI ID by running the following command:

	```	
	aws ec2 describe-images --owners amazon --filters 'Name=name,Values=amzn2-ami-hvm-2.0.????????-x86_64-gp2' 'Name=state,Values=available' --output json | jq -r '.Images | sort_by(.CreationDate) | last(.[]).ImageId'
	```

1. Update **%KeyName%** with your ssh key pair name.

1. Update **%UserData%** with the contents of **user-data.base64.txt**.

1. Save the file.

1. Create the launch template from the launch template config you just saved.

	```
	aws ec2 create-launch-template --launch-template-name runningAmazonEC2WorkloadsAtScale --version-description dev --launch-template-data file://launch-template-data.json
	```
	
1. Browse to the [Launch Templates console](https://console.aws.amazon.com/ec2/v2/home?#LaunchTemplates:sort=launchTemplateId) and check out your newly created launch template.

### 6\. Deploy the database with Amazon RDS

Amazon Relational Database Service (Amazon RDS) makes it easy to set up, operate, and scale a relational database in the cloud. It provides cost-efficient and resizable capacity while automating time-consuming administration tasks such as hardware provisioning, database setup, patching and backups. It frees you to focus on your applications so you can give them the fast performance, high availability, security and compatibility they need.

1. Edit the file **rds.json**. Update the values **%dbSecurityGroup%** and **%dbSubnetGroup%** from the CloudFormation stack outputs. Save the file.

1. Create the RDS instance:

	```
	aws rds create-db-instance --cli-input-json file://rds.json
	```
	
1. Browse to the [Amazon RDS console](https://console.aws.amazon.com/rds/home?#dbinstances:) to monitor your database deployment. Creating the database will take a few minutes. To save time, you can move onto the next step. You'll come back to check on the database creation in a later step.

### 7\. Deploy the load balancer

A load balancer serves as the single point of contact for clients. The load balancer distributes incoming application traffic across multiple targets, such as EC2 instances, in multiple Availability Zones. This increases the availability of your application. You add one or more listeners to your load balancer.

A listener checks for connection requests from clients, using the protocol and port that you configure, and forwards requests to one or more target groups, based on the rules that you define. Each rule specifies a target group, condition, and priority. When the condition is met, the traffic is forwarded to the target group. You must define a default rule for each listener, and you can add rules that specify different target groups based on the content of the request (also known as content-based routing).

Each target group routes requests to one or more registered targets, such as EC2 instances, using the protocol and port number that you specify. You can register a target with multiple target groups. You can configure health checks on a per target group basis. Health checks are performed on all targets registered to a target group that is specified in a listener rule for your load balancer.

1. Edit **application-load-balancer.json** and update the values of **%publicSubnet1%**, **%publicSubnet2%**, and **%loadBalancerSecurityGroup%** from the CloudFormation stack outputs. Save the file. Create the application load balancer:

	```
	aws elbv2 create-load-balancer --cli-input-json file://application-load-balancer.json
	```

	>Plese note the ARN of the application load balancer for use in an upcoming step.

1. Browse to the [Load Balancer console](https://console.aws.amazon.com/ec2/v2/home#LoadBalancers:sort=loadBalancerName) to check out your newly created load balancer.

1. 	Edit **target-group.json** and update the value of **%vpc%** from the CloudFormation stack outputs. Save the file. Create the target group:

	```
	aws elbv2 create-target-group --cli-input-json file://target-group.json
	```

	>Please note the ARN of the target group for use in upcoming steps.

1. Edit **modify-target-group.json** and update the value of **%TargetGroupArn%** with the ARN. Save the file. Modify the target group:

	```
	aws elbv2 modify-target-group-attributes --cli-input-json file://modify-target-group.json
	```

1. Browse to the [Target Group console](https://console.aws.amazon.com/ec2/v2/home#TargetGroups:sort=targetGroupName) to check out your newly created target group.

1. Edit **listener.json** and update the values of **%LoadBalancerArn%** and **%TargetGroupArn%** from the previous steps. Save the file. Create the listener:

	```
	aws elbv2 create-listener --cli-input-json file://listener.json
	```

1. Browse to the [Load Balancer console](https://console.aws.amazon.com/ec2/v2/home#LoadBalancers:sort=loadBalancerName) to check out your newly created listener by selecting your load balancer and clicking on the **Listeners** tab.

### 8\. Create an auto scaling group and associate it with the load balancer

Amazon EC2 Auto Scaling helps you maintain application availability and allows you to dynamically scale your Amazon EC2 capacity up or down automatically according to conditions you define. You can use Amazon EC2 Auto Scaling for fleet management of EC2 instances to help maintain the health and availability of your fleet and ensure that you are running your desired number of Amazon EC2 instances. You can also use Amazon EC2 Auto Scaling for dynamic scaling of EC2 instances in order to automatically increase the number of Amazon EC2 instances during demand spikes to maintain performance and decrease capacity during lulls to reduce costs. Amazon EC2 Auto Scaling is well suited both to applications that have stable demand patterns or that experience hourly, daily, or weekly variability in usage.

1. Edit **asg.json** update the values of **%TargetGroupArn%** from the previous steps.

1. Update the values of **%publicSubnet1%** and **%publicSubnet2%** from the CloudFormat stack outputs.

1. Save the file and create the auto scaling group:

	```
	aws autoscaling create-auto-scaling-group --cli-input-json file://asg.json
	```
	
	>Note: This command will not return any output if it is successful.
	
1. Browse to the [Auto Scaling console](https://console.aws.amazon.com/ec2/autoscaling/home#AutoScalingGroups:view=details) and check out your newly created auto scaling group. Take a look at the instances it has deployed.

### 9\. Seed the database with application data

1. Browse to the [Amazon RDS console](https://console.aws.amazon.com/rds/home?#dbinstances:) to monitor your database deployment. Click on your database name. Under **Summary**, the **DB instance status** should be **available**. If it isn't quite ready (perhaps still doing the initial backup), you can hit refresh every couple of minutes and wait for it to be in the **available** state.

1. In the **Connect** section, find the **Endpoint** of the database instance (e.g. **runningamazonec2workloadsatscale.ckhifpaueqm7.us-east-1.rds.amazonaws.com**
).

1. Seed the database for the application environment. Replace **%endpoint%** with the database instance endpoint noted in the last step:

	```
	mysql -h %endpoint% -u dbadmin --password=db-pass-2020 -f koel < koel.sql
	```
	>Note: This command will not return any output if it is successful.
	
### 10\. Deploy the application to the automatic scaling group with CodeDeploy

An application specification file (AppSpec file), which is unique to AWS CodeDeploy, is a YAML-formatted or JSON-formatted file. The AppSpec file is used to manage each deployment as a series of lifecycle event hooks, which are defined in the file. The AppSpec file is used to:
	
* Map the source files in your application revision to their destinations on the instance.

* Specify custom permissions for deployed files.

* Specify scripts to be run on each instance at various stages of the deployment process.

You can learn more about the AppSpec File Structure [here](https://docs.aws.amazon.com/codedeploy/latest/userguide/reference-appspec-file-structure.html).

You will now deploy your application to the EC2 instances launched by the auto scaling group.

1. Take a moment to browse and view the CodeDeploy structure for your application, located in the **codedeploy** directory.

1. You'll need to modify the CodeDeploy deployment scripts in order to implement using the RDS database instance. Edit **codedeploy/scripts/configure_db.sh**. Replace **%endpoint%** with the **Endpoint** of the database instance (e.g. **runningamazonec2workloadsatscale.ckhifpaueqm7.us-east-1.rds.amazonaws.com**
). Save the file.

1. Then clone the Koel GitHub repo:

	```
	git clone https://github.com/phanan/koel.git
	
	cd koel && git checkout v3.7.2
	```
	>Note: you'll get an update about being in 'detached HEAD' state. This is normal.
	
1. Next, copy the CodeDeploy configs into the root level of the koel application directory:

	```
	cp -avr ../codedeploy/* .
	```

1. After reviewing and getting comfortable with the CodeDeploy configs, go ahead and create the CodeDeploy application:

	```
	aws deploy create-application --application-name koelApp
	```

1. Browse to the [AWS CodeDeploy console](https://console.aws.amazon.com/codesuite/codedeploy/applications), make sure your region is selected in the upper right-hand corner dropdown, and then click on your application to check out your newly created application.

	>Note: The CodeDeploy console will not default to your current region. Please make sure to click on **Select a Region** in the upper right-hand corner and select your region in the dropdown.
	
1. Next, push the application to the CodeDeploy S3 bucket. Be sure to replace **%codeDeployBucket%** with the value in the CloudFormation stack outputs:

	```
	aws deploy push --application-name koelApp --s3-location s3://%codeDeployBucket%/koelApp.zip --no-ignore-hidden-files
	```
	>Note: You will get output similiar to the following. This is normal and correct:
	
	>*To deploy with this revision, run: aws deploy create-deployment --application-name koelApp --s3-location bucket=runningamazonec2workloadsatscale-codedeploybucket-11wv3ggxcni40,key=koelApp.zip,bundleType=zip,eTag=870b90e201bdca3a06d1b2c6cfcaab11-2 --deployment-group-name <deployment-group-name> --deployment-config-name <deployment-config-name> --description <description>*
	
1. Find the value of **codeDeployBucket** in the CloudFormation stack outputs. This is the bucket you're using for your code deployments. Browse to the [S3 console](https://s3.console.aws.amazon.com/s3/home) and click on the bucket. You should see your application deployment bundle inside the bucket.

1. Create the CodeDeploy deployment group by editing **deployment-group.json** and replacing the value of **%codeDeployServiceRole%** from the CloudFormation stack outputs, and then running:

	```
	cd ..
	
	aws deploy create-deployment-group --cli-input-json file://deployment-group.json
	```

1. Browse to the [AWS CodeDeploy console](https://console.aws.amazon.com/codesuite/codedeploy/applications), make sure your region is selected in the upper right-hand corner dropdown, click on your application, and then click on the **Deployment groups** tab to check out your newly created deployment group.

	>Note: The CodeDeploy console will not default to your current region. Please make sure to click on **Select a Region** in the upper right-hand corner and select your region in the dropdown.

1. Finally, deploy the application by editing **deployment.json** and replacing the value of **%codeDeployBucket%** from the CloudFormation stack outputs, and then running:

	```
	aws deploy create-deployment --cli-input-json file://deployment.json
	```
	
	>Note the **deploymentId**.
	
1. Browse to the [AWS CodeDeploy console](https://console.aws.amazon.com/codesuite/codedeploy/deployments), make sure your region is selected in the upper right-hand corner dropdown, and then click on your **Deployment ID** to monitor your application deployment. At the bottom under **Deployment lifecycle events**, you will see a list of the EC2 instances belonging to your auto scaling group. To monitor the individual deployments to each of the instances, click on **View Events**.

	>Note: The CodeDeploy console will not default to your current region. Please make sure to click on **Select a Region** in the upper right-hand corner and select your region in the dropdown.

1. As the application is successfully deployed to the instances, they will pass their target group health checks and be marked as healthy in the target group status. Browse to the [Target Group console](https://console.aws.amazon.com/ec2/v2/home#TargetGroups:sort=targetGroupName), select your target group, and click on the **Targets** tab.

1. Once one or more instances are marked with a status of healthy, browse to the [Load Balancer console](https://console.aws.amazon.com/ec2/v2/home#LoadBalancers:sort=loadBalancerName), select your load balancer, and copy the **DNS name** (URL) of your load balancer (e.g. http://runningAmazonEC2WorkloadsAtScale-115077449.us-east-1.elb.amazonaws.com).

1. Open your web browser and browse to the **DNS name** (URL). You will see the login page to your application. Login in with the default email address '**admin@example.com**' and default password '**admin-pass**'.

1. The EFS file system is mounted on every instance at **/var/www/media** in order to create a shared location for your audio files. Mount the EFS file system in the Cloud9 environment and copy some mp3s to the file system. Replace **%fileSystem** with the value from the CloudFormation stack outputs:

	```
	mkdir -p ~/environment/media

	sudo mount -t efs %fileSystem%:/ ~/environment/media
	
	sudo chown ec2-user. ~/environment/media
	
	sudo cp -av *.mp3 ~/environment/media
	```	
	
1. Back in Koel, under **MANAGE**, click on **Settings**. Click on **Scan**. Play around and enjoy some audio on your music service.

1. [Optional] If you'd like, find a few more mp3s on the web and upload them to the directory **~/environment/media** in the Cloud9 environment. After uploading them, be sure to re-scan the media directory.

### 11\. Scale the application with a scheduled scaling action

Scaling based on a schedule allows you to scale your application in response to predictable load changes. For example, every week the traffic to your web application starts to increase on Wednesday, remains high on Thursday, and starts to decrease on Friday. You can plan your scaling activities based on the predictable traffic patterns of your web application.

To configure your Auto Scaling group to scale based on a schedule, you create a scheduled action, which tells Amazon EC2 Auto Scaling to perform a scaling action at specified times. To create a scheduled scaling action, you specify the start time when the scaling action should take effect, and the new minimum, maximum, and desired sizes for the scaling action. At the specified time, Amazon EC2 Auto Scaling updates the group with the values for minimum, maximum, and desired size specified by the scaling action.

1. Edit **asg-scheduled-scaling.json** and replace **%StartTime%** with a UTC timestamp of a few minutes in the future. For example: **2018-11-11T12:20:00**. You can use this [site](https://timestampgenerator.com/) to help. Look for the **Atom** format. Save the file.

1. Schedule the scaling action:

	```
	aws autoscaling put-scheduled-update-group-action --cli-input-json file://asg-scheduled-scaling.json
	```
	
	>Note: This command will not return any output if it is successful.

1. Browse to the [Auto Scaling console](https://console.aws.amazon.com/ec2/autoscaling/home#AutoScalingGroups:view=details) and check out your newly created scheduled scaling action in the **Scheduled Actions** tab. Wait for the time you chose, and take a look at the instances it has deployed by checking the **Activity History** tab and the **Instances** tab.

1. Browse to the [AWS CodeDeploy console](https://console.aws.amazon.com/codesuite/codedeploy/deployments), make sure your region is selected in the upper right-hand corner dropdown, and notice that CodeDeploy will automatically deploy the application to new instances launched by the auto scaling group.

	>Note: The CodeDeploy console will not default to your current region. Please make sure to click on **Select a Region** in the upper right-hand corner and select your region in the dropdown.

### 12\. Dynamically scale the application with an automatic scaling policy

When you configure dynamic scaling, you must define how to scale in response to changing demand. For example, you have a web application that currently runs on two instances and you do not want the CPU utilization of the Auto Scaling group to exceed 70 percent. You can configure your Auto Scaling group to scale automatically to meet this need. The policy type determines how the scaling action is performed.

Target tracking scaling policies simplify how you configure dynamic scaling. You select a predefined metric or configure a customized metric, and set a target value. Amazon EC2 Auto Scaling creates and manages the CloudWatch alarms that trigger the scaling policy and calculates the scaling adjustment based on the metric and the target value. The scaling policy adds or removes capacity as required to keep the metric at, or close to, the specified target value. In addition to keeping the metric close to the target value, a target tracking scaling policy also adjusts to the fluctuations in the metric due to a fluctuating load pattern and minimizes rapid fluctuations in the capacity of the Auto Scaling group.

1. Review **asg-automatic-scaling.json** to understand the options. There are no changes to be made. Then go ahead and apply the scaling policy:

	```
	aws autoscaling put-scaling-policy --cli-input-json file://asg-automatic-scaling.json
	```

1. Browse to the [Auto Scaling console](https://console.aws.amazon.com/ec2/autoscaling/home#AutoScalingGroups:view=details) and check out your newly created scaling policy in the **Scaling Policies** tab. Notice that in a few minutes, it will begin to scale down the instances that were previously scaled up by the scheduled scaling action in order to satisfy the target tracking metrics defined in the automatic scaling policy (check the **Activity History** tab and the **Instances** tab).

### 13\. Stress the application with AWS Systems Manager to trigger the automatic scaling policy

AWS Systems Manager provides you safe, secure remote management of your instances at scale without logging into your servers, replacing the need for bastion hosts, SSH, or remote PowerShell. It provides a simple way of automating common administrative tasks across groups of instances such as registry edits, user management, and software and patch installations. Through integration with AWS Identity and Access Management (IAM), you can apply granular permissions to control the actions users can perform on instances. All actions taken with Systems Manager are recorded by AWS CloudTrail, allowing you to audit changes throughout your environment.

You will now emulate CPU stress on the instances in your automatic scaling group by issuing a remote command to each instance.

1. Review **ssm-stress.json** to understand the options. There are no changes to be made. Then go ahead and send the command:

	```
	aws ssm send-command --cli-input-json file://ssm-stress.json
	```

1. Browse to the [AWS Systems Manager console](https://console.aws.amazon.com/systems-manager/run-command/executing-commands) to monitor the status of your run  commands.

1. Browse to the [CloudWatch console](https://console.aws.amazon.com/cloudwatch/home?#alarm:alarmFilter=ANY) to monitor the status of your alarms configured by the target tracking policy.

1. Browse to the [Auto Scaling console](https://console.aws.amazon.com/ec2/autoscaling/home#AutoScalingGroups:view=details) and watch the activity history. Notice that in a few minutes, it will begin to scale up the instances according to the CloudWatch alarms the target tracking policy has configured for you (check the **Activity History** tab and the **Instances** tab).

1. Browse to the [AWS CodeDeploy console](https://console.aws.amazon.com/codesuite/codedeploy/deployments), make sure your region is selected in the upper right-hand corner dropdown, and notice that CodeDeploy will automatically deploy the application to new instances launched by the auto scaling group.

	>Note: The CodeDeploy console will not default to your current region. Please make sure to click on **Select a Region** in the upper right-hand corner and select your region in the dropdown.

* * *

## Finished!  
Congratulations on completing the workshop...*or at least giving it a good go*!  This is the workshop's permananent home, so feel free to revisit as often as you'd like.  In typical Amazon fashion, we'll be listening to your feedback and iterating to make it better.  If you have feedback, we're all ears!  Make sure you clean up after the workshop, so you don't have any unexpected charges on your next monthly bill.  

## Workshop Cleanup

1. Working backwards, delete all manually created resources.

	```
	aws autoscaling delete-auto-scaling-group --auto-scaling-group-name runningAmazonEC2WorkloadsAtScale --force-delete
	
	aws deploy delete-deployment-group --application-name koelApp --deployment-group-name koelDepGroup
	
	aws deploy delete-application --application-name koelApp
	
	aws s3 rm s3://%codeDeployBucket% --recursive
		
	aws elbv2 delete-load-balancer --load-balancer-arn %loadBalancerArn%
	
	aws elbv2 delete-target-group --target-group-arn %targetGroupArn%
	
	aws rds delete-db-instance --db-instance-identifier runningAmazonEC2WorkloadsAtScale --skip-final-snapshot
	
	aws ec2 delete-launch-template --launch-template-name runningAmazonEC2WorkloadsAtScale
	```
	
1. Finally, delete the CloudFormation stack itself.
	
	```
	aws cloudformation delete-stack --stack-name runningAmazonEC2WorkloadsAtScale
	```

## Acknolwedgements

A big thank you to [Phan An](https://www.phanan.net/) for creating and maintaining [Koel](https://koel.phanan.net/) and for allowing Koel to be used in this workshop.

## Appendix  

### Resources
Here are additional resources to learn more:

* [Amazon EC2 Auto Scaling](https://aws.amazon.com/ec2/autoscaling/)
* [Amazon EC2 Spot Instances](https://aws.amazon.com/ec2/spot)
* [Amazon EC2 Spot Labs GitHub Repo](https://github.com/awslabs/ec2-spot-labs/)

### Articles
* [Amazon EC2 Auto Scaling Groups With Multiple Instance Types & Purchase Options](https://aws.amazon.com/blogs/aws/new-ec2-auto-scaling-groups-with-multiple-instance-types-purchase-options/)
* [Taking Advantage of Amazon EC2 Spot Instance Interruption Notices](https://aws.amazon.com/blogs/compute/taking-advantage-of-amazon-ec2-spot-instance-interruption-notices/)


