# Running Amazon EC2 Workloads at Scale: Workshop guide
  
  
## Overview
[UPDATE] This workshop is designed to get you familiar with...[/UPDATE]

## Requirements, notes, and legal
1. To complete this workshop, have access to an AWS account with administrative permissions. An IAM user with administrator access (**arn:aws:iam::aws:policy/AdministratorAccess**) will do nicely.

1. This workshop is self-paced. The instructions will primarily be given using the [AWS Command Line Interface (CLI)](https://aws.amazon.com/cli) - this way the guide will not become outdated as changes or updates are made to the AWS Management Console. However, most steps in the workshop can be done in the AWS Management Console directly. Feel free to use whatever is comfortable for you.

1. While the workshop provides step by step instructions, please do take a moment to look around and understand what is happening at each step. The workshop is meant as a getting started guide, but you will learn the most by digesting each of the steps and thinking about how they would apply in your own environment. You might even consider experimenting with the steps to challenge yourself.

1. This workshop has been designed to run in any public AWS Region.
	>Note: If you are attending an event, please run in the region suggested by the facilitators of the workshop.

1. Make sure you have a valid Amazon EC2 key pair and record the key pair name in the region you are operating in before you begin. To see your key pairs, open the Amazon EC2 console, then click Key Pairs in the navigation pane.
	>Note: If you don't have an Amazon EC2 key pair, you must create the key pair in the same region where you are creating the stack. For information about creating a key pair, see [Getting an SSH Key Pair](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-key-pairs.html#having-ec2-create-your-key-pair) in the Amazon EC2 User Guide for Linux Instances. 

1. During this workshop, you will install software (and dependencies) on the Amazon EC2 instances launched in your account. The software packages and/or sources you will install will be from the [Amazon Linux 2](https://aws.amazon.com/amazon-linux-2/) distribution as well as from third party repositories and sites. Please review and decide your comfort with installing these before continuing.


## [NEED TO UPDATE] Architecture

In this workshop, you will deploy the following:

* An Amazon Virtual Private Cloud (Amazon VPC) with subnets in two Availability Zones
* An Application Load Balancer (ALB) with a listener and target group
* An Amazon CloudWatch Events rule
* An AWS Lambda function
* An Amazon Simple Notification Service (SNS) topic
* Associated IAM policies and roles for all of the above
* An Amazon EC2 Spot Fleet request diversified across both Availability Zones using a couple of recent Spot Fleet features: Elastic Load Balancing integration and Tagging Spot Fleet Instances

When any of the Spot Instances receives an interruption notice, Spot Fleet sends the event to CloudWatch Events. The CloudWatch Events rule then notifies both targets, the Lambda function and SNS topic. The Lambda function detaches the Spot Instance from the Application Load Balancer target group, taking advantage of a full two minutes of connection draining before the instance is interrupted. The SNS topic also receives a message, and is provided as an example for the reader to use as an exercise (***hint***: have it send you an email or an SMS message).

Here is a diagram of the resulting architecture:

![](images/interruption_notices_arch_diagram.jpg)
## [/NEED TO UPDATE]

## Let's Begin!  

### 1\. Launch the CloudFormation stack

To save time on the initial setup, a CloudFormation template will be used to create the Amazon VPC with subnets in two Availability Zones, as well various supporting resources such as IAM policies and roles, security groups, S3 buckets, an EFS file system, and a Cloud9 IDE environment for you to run the steps for the workshop in.

#### To create the stack

1. You can view and download the CloudFormation temlate from GitHub [here](https://raw.githubusercontent.com/awslabs/ec2-spot-labs/master/workshops/running-amazon-ec2-workloads-at-scale/running-amazon-ec2-workloads-at-scale.yaml).

1. Take a moment to review the CloudFormation template so you understand the resources it will be creating.

1. Sign in to the AWS Management Console and open the AWS CloudFormation console at [https://console.aws.amazon.com/cloudformation](https://console.aws.amazon.com/cloudformation).
>Note: Make sure you are in the right region!

1. Click **Create Stack**.

1. In the **Specify template** section, select **Upload a template file**. Click **Choose file** and, select the template you downloaded in step 1.

1. Click **Next**.

1. In the **Specify stack details** section, enter a **Stack name**. For example, use *runningAmazonEC2WorkloadsAtScale*. The stack name cannot contain spaces.

1. [Optional] In the **Parameters** section, optionally change the **sourceCidr** to restrict instance ssh/http access and load balancer http access.

1. Click **Next**.

1. In **Configure stack options**, leave the default settings.

1. Click **Next**.

1. Review the information for the stack. At the bottom under **Capabilities**, select **I acknowledge that AWS CloudFormation might create IAM resources**. When you're satisfied with the settings, click **Create stack**.

Your stack might take several minutes to create—but you probably don't want to just sit around waiting. After you complete the Create Stack wizard, AWS CloudFormation begins creating the resources that are specified in the template. Your new stack appears in the list at the top portion of the CloudFormation console. Its status should be **CREATE\_IN\_PROGRESS**. You can see detailed status for a stack by viewing its events.

#### Monitor the progress of stack creation

1. On the AWS CloudFormation console, select the stack in the list.

1. In the stack details pane, click the **Events** tab. The console automatically refreshes the event list with the most recent events every 60 seconds.

The **Events** tab displays each major step in the creation of the stack sorted by the time of each event, with latest events on top.

The **CREATE\_IN\_PROGRESS** event is logged when AWS CloudFormation reports that it has begun to create the resource. The **CREATE_COMPLETE** event is logged when the resource is successfully created.

When AWS CloudFormation has successfully created the stack, you will see the following event at the top of the Events tab:

2018-04-24 19:17 UTC-7 **CREATE_COMPLETE** AWS::CloudFormation::Stack

#### Use your stack resources

In this workshop, you'll need to reference the resources created by the CloudFormation stack.

1. On the AWS CloudFormation console, select the stack in the list.

1. In the stack details pane, click the **Outputs** tab.

It is recommended that you keep this window open so you can easily refer to the outputs and resources throughout the workshop.

### 2\. Get familiar with the AWS Cloud9 environment

AWS Cloud9 comes with a terminal that includes sudo privileges to the managed Amazon EC2 instance that is hosting your development environment and a preauthenticated AWS Command Line Interface. This makes it easy for you to quickly run commands and directly access AWS services.

An AWS Cloud9 environment was launched as a part of the CloudFormation stack (you may have noticed a second CloudFormation stack created by Cloud9). You'll be using this Cloud9 environment to execute the steps in the workshop.

1. Find the name of the AWS Cloud9 environment that was launched as a part of the CloudFormation stack outputs.

1. Sign in to the AWS Cloud9 console at [https://console.aws.amazon.com/cloud9/](https://console.aws.amazon.com/cloud9/).

1. Find the Cloud9 environment in **Your environments**, and click **Open IDE**.

1. Take a moment to get familiar with the Cloud9 environment. You can even take a quick tour of Cloud9 [here](https://docs.aws.amazon.com/cloud9/latest/user-guide/tutorial.html#tutorial-tour-ide) if you'd like.

### 3\. Clone the workshop GitHub repo

In order to execute the steps in the workshop, you'll need to clone the workshop GitHub repo.

1. In the Cloud9 IDE terminal, run the following command:

	```
	git clone https://github.com/awslabs/ec2-spot-labs.git
	```
1. Change into the workshop directory:

	```
	cd ec2-spot-labs/workshops/running-amazon-ec2-workloads-at-scale
	```

1. Feel free to browse around. You can also browse the directory structure in the **Environment** tab, and even edit files directly there. Note there is a **dev** directory and a **prod** directory. You'll be using these in the steps below.

### 4\. Create the launch template for the development environment

EC2 Launch Templates reduce the number of steps required to create an instance by capturing all launch parameters within one resource. 

You can create a launch template that contains the configuration information to launch an instance. Launch templates enable you to store launch parameters so that you do not have to specify them every time you launch an instance. For example, a launch template can contain the AMI ID, instance type, and network settings that you typically use to launch instances. When you launch an instance using the Amazon EC2 console, an AWS SDK, or a command line tool, you can specify the launch template to use.

1. You'll use the **UserData** field of a launch template to install the AWS CodeDeploy agent on instances launched from the launch template. Change into the **dev** directory and edit the file **user-data.txt**. Review how it will install packages and then update **%awsRegionId%** with the value from the CloudFormation stack outputs. Save the file.

1. Convert the file to base64 for use in the launch template:

	```
	base64 --wrap=0 user-data.txt > user-data.base64.txt
	```
	
1. Next, edit **launch-template-data.json**.

1. Update the following values from the CloudFormation stack outputs: **%instanceProfile%** and **%instanceSecurityGroup%**.

1. Update **%ami-id%** with the AMI ID for the latest version of Amazon Linux 2 in the AWS region you launched. You can find the AMI ID by running the following command:

	```
	sudo yum -y install jq
	
	aws ec2 describe-images --owners amazon --filters 'Name=name,Values=amzn2-ami-hvm-2.0.????????-x86_64-gp2' 'Name=state,Values=available' --output json | jq -r '.Images | sort_by(.CreationDate) | last(.[]).ImageId'
	```

1. Update **%KeyName%** with your ssh key pair name.

1. Update **%UserData%** with the contents of **user-data.base64.txt**.

1. Save the file.

1. Create the launch template from the launch template config you just saved.

	```
	aws ec2 create-launch-template --launch-template-name runningAmazonEC2WorkloadsAtScale --version-description dev --launch-template-data file://launch-template-data.json
	```
	
1. Browse to the Launch Templates console at [https://console.aws.amazon.com/ec2/v2/home?#LaunchTemplates:sort=launchTemplateId](https://console.aws.amazon.com/ec2/v2/home?#LaunchTemplates:sort=launchTemplateId) and check out your newly created launch template.

### 5\. Launch EC2 Spot Instance with EC2 Fleet for the development environment

Amazon EC2 Fleet is an API that simplifies the provisioning of Amazon EC2 capacity across different Amazon EC2 instance types, Availability Zones and across On-Demand, Amazon EC2 Reserved Instances (RI) and Amazon EC2 Spot purchase models. With a single API call, now you can provision capacity across EC2 instance types and across purchase models to achieve desired scale, performance and cost.

You'll now launch an EC2 Fleet for your dev environment. The EC2 Fleet will consist of a single EC2 Spot Instance, and the fleet will be able to find capacity in any of the 6 available capacity pools.

1. Edit **ec2-fleet.json**. Take a moment to review the config and understand the options.

1. Update all references of **%publicSubnet1%** and **%publicSubnet2%** (3 each) with the values from the CloudFormation stack outputs. Save the file. Create the EC2 Fleet:

	```
	aws ec2 create-fleet --cli-input-json file://ec2-fleet.json
	```
	
1. Browse to the EC2 Spot console at [https://console.aws.amazon.com/ec2sp/v1/spot/home](https://console.aws.amazon.com/ec2sp/v1/spot/home) and check out your newly created EC2 Spot Instance.

### 6\. Deploy the application with CodeDeploy in the development environment

AWS CodeDeploy is a fully managed deployment service that automates software deployments to a variety of compute services such as Amazon EC2, AWS Lambda, and your on-premises servers. AWS CodeDeploy makes it easier for you to rapidly release new features, helps you avoid downtime during application deployment, and handles the complexity of updating your applications. You can use AWS CodeDeploy to automate software deployments, eliminating the need for error-prone manual operations. The service scales to match your deployment needs, from a single Lambda function to thousands of EC2 instances.

You will now deploy a development environment of Koel to the Spot Instance launched by EC2 Fleet.

1. From the **dev** directory, first clone the Koel GitHub repo:

	```
	git clone https://github.com/phanan/koel.git
	
	cd koel && git checkout v3.7.2
	```
	>Note: you'll get an update about being in 'detached HEAD' state. This is normal.
	
1. Next, copy the CodeDeploy configs into the root level of the application directory:

	```
	cp -avr ../codedeploy/* .
	```

1. The CodeDeploy configs do not need any modification to use them. However, you should take the opportunity to review them to understand the structure and contents. Open and review **appspec.yml**, and all corresponding files in the **scripts/** directory: **build\_and\_install.sh**, **configure_db.sh**, **configure\_httpd\_php.sh**, **install_dependencies.sh**, **start_services.sh**, and **stop_services.sh**.

1. A couple of additional supporting config files were also copied into place: **koel.conf**, which is the Apache virtual host config, and **koel.sql**, which is a seed of the Koel database. Please take a moment to review them as well. 

1. After reviewing and getting comfortable with the CodeDeploy configs, go ahead and Create the CodeDeploy application:

	```
	aws deploy create-application --application-name koelAppDev
	```

1. Browse to the AWS CodeDeploy console at [https://console.aws.amazon.com/codesuite/codedeploy/applications](https://console.aws.amazon.com/codesuite/codedeploy/applications) to check out your newly created application.
	
1. Next, push the application to the CodeDeploy S3 bucket. Be sure to replace **%codeDeployBucket%** with the value in the CloudFormation stack outputs:

	```
	aws deploy push --application-name koelAppDev --s3-location s3://%codeDeployBucket%/koelAppDev.zip --no-ignore-hidden-files
	```

1. Browse to the S3 console at [https://s3.console.aws.amazon.com/s3/home](https://s3.console.aws.amazon.com/s3/home) to check out your newly created application bundle. The bucket name is the **codeDeployBucket** value in the CloudFormation stack outputs.

1. Create the CodeDeploy deployment group by editing **deployment-group.json** and replacing the value of **%codeDeployServiceRole%** from the CloudFormation stack outputs, and then running:

	```
	cd ..
	
	aws deploy create-deployment-group --cli-input-json file://deployment-group.json
	```
	
	>Note: CodeDeploy knows which instances to deploy to by filtering on EC2 instance tags. The tags are configured in the launch template and filtered on in the deployment group.
	
1. Browse to the AWS CodeDeploy console at [https://console.aws.amazon.com/codesuite/codedeploy/applications](https://console.aws.amazon.com/codesuite/codedeploy/applications) to check out your newly created deployment group.

1. Finally, deploy the application by editing **deployment.json** and replacing the value of **%codeDeployBucket%** from the CloudFormation stack outputs, and then running:

	```
	aws deploy create-deployment --cli-input-json file://deployment.json
	```
	
1. Browse to the AWS CodeDeploy console at [https://console.aws.amazon.com/codesuite/codedeploy/deployments](https://console.aws.amazon.com/codesuite/codedeploy/deployments) to monitor your application deployment.

1. Once the deploy is complete, browse to the public DNS of the dev Spot Instance launched by EC2 Fleet and login. The default email address is **admin@example.com** and default password is **admin-pass**.

1. Find some mp3s on the interwebs and upload them to **/var/www/media** on the dev instance. *****THIS STEP NEEDS MORE DETAILS*****

1. Under **MANAGE**, click on **Settings**. Click on **Scan**. Play around and enjoy some tunes on your music service.

### 7\. Deploy the production environment database with Amazon RDS

In the development environment, you installed a mariadb database server on the local development instance. In production, you'll want to install to a shared database server so that you can scale your instances behind a load balancer.

Amazon Relational Database Service (Amazon RDS) makes it easy to set up, operate, and scale a relational database in the cloud. It provides cost-efficient and resizable capacity while automating time-consuming administration tasks such as hardware provisioning, database setup, patching and backups. It frees you to focus on your applications so you can give them the fast performance, high availability, security and compatibility they need.

1. Change into the **prod** directory

	```
	cd prod
	```

1. Edit the file **rds.json**. Update the values **%dbSecurityGroup%** and **%dbSubnetGroup%**.

	>Please note the **MasterUsername** and **MasterUserPassword**, as you'll need them in a later step.

1. Save the file and create the RDS instance:

	```
	aws rds create-db-instance --cli-input-json file://rds.json
	```
	
1. Browse to the Amazon RDS console at [https://console.aws.amazon.com/rds/home?#dbinstances:](https://console.aws.amazon.com/rds/home?#dbinstances:) to monitor your database deployment. Wait for the **DB instance status** to become **available**.

	> Please note the **Endpoint** of the database instance (e.g. **runningamazonec2workloadsatscale.ckhifpaueqm7.us-east-1.rds.amazonaws.com**
).

1. Seed the database for the production environment. Replace **%endpoint%** with the database instance endpoint noted in the last step, and use the **MasterUserPassword** noted above when prompted:

	```
	mysql -h %endpoint% -u dbadmin -p -f koel < koel.sql
	```

### 7\. Deploy the load balancer for the production environment

In the development environment, you didn't need a load balancer since you were just deploying to a single instance. In production, you'll want to install a load balancer so that you can scale your instances behind it.

A load balancer serves as the single point of contact for clients. The load balancer distributes incoming application traffic across multiple targets, such as EC2 instances, in multiple Availability Zones. This increases the availability of your application. You add one or more listeners to your load balancer.

A listener checks for connection requests from clients, using the protocol and port that you configure, and forwards requests to one or more target groups, based on the rules that you define. Each rule specifies a target group, condition, and priority. When the condition is met, the traffic is forwarded to the target group. You must define a default rule for each listener, and you can add rules that specify different target groups based on the content of the request (also known as content-based routing).

Each target group routes requests to one or more registered targets, such as EC2 instances, using the protocol and port number that you specify. You can register a target with multiple target groups. You can configure health checks on a per target group basis. Health checks are performed on all targets registered to a target group that is specified in a listener rule for your load balancer.

1. Edit **application-load-balancer.json** and update the values of **%publicSubnet1%**, **%publicSubnet2%**, and **%loadBalancerSecurityGroup%** from the CloudFormation stack outputs. Save the file. Create the application load balancer:

	```
	aws elbv2 create-load-balancer --cli-input-json file://application-load-balancer.json
	```

	>Plese note the ARN of the application load balancer for use in an upcoming step.

1. Browse to the Load Balancer console at [https://console.aws.amazon.com/ec2/v2/home#LoadBalancers:sort=loadBalancerName](https://console.aws.amazon.com/ec2/v2/home#LoadBalancers:sort=loadBalancerName) to check out your newly created load balancer.

1. 	Edit **target-group.json** and update the value of **%vpc%** from the CloudFormation stack outputs. Save the file. Create the target group:

	```
	aws elbv2 create-target-group --cli-input-json file://target-group.json
	```

	>Please note the ARN of the target group for use in an upcoming step.

1. Edit **modify-target-group.json** and update the value of **%TargetGroupArn%** with the ARN. Save the file. Modify the target group:

	```
	aws elbv2 modify-target-group-attributes --cli-input-json file://modify-target-group.json
	```

1. Browse to the Target Group console at [https://console.aws.amazon.com/ec2/v2/home#TargetGroups:sort=targetGroupName](https://console.aws.amazon.com/ec2/v2/home#TargetGroups:sort=targetGroupName) to check out your newly created target group.

1. Edit **listener.json** and update the values of **%LoadBalancerArn%** and **%TargetGroupArn%** from the previous steps. Save the file. Create the listener:

	```
	aws elbv2 create-listener --cli-input-json file://listener.json
	```

1. Browse to the Load Balancer console at [https://console.aws.amazon.com/ec2/v2/home#LoadBalancers:sort=loadBalancerName](https://console.aws.amazon.com/ec2/v2/home#LoadBalancers:sort=loadBalancerName) to check out your newly created listener.

### 8\. Create a new version of the launch template for the production environment

For each launch template, you can create one or more numbered launch template versions. Each version can have different launch parameters. When you launch an instance from a launch template, you can use any version of the launch template. If you do not specify a version, the default version is used. You can set any version of the launch template as the default version—by default, it's the first version of the launch template.

You'll make a new version of the launch template for use in the production environment.

1. Review **launch-template-data.json**. There are no changes to be made, but note that you are referencing the previous version of the launch template and making updates to the tags.

1. Create a new version of the launch template:

	```
	aws ec2 create-launch-template-version --cli-input-json file://launch-template-data.json
	```
	
1. Browse to the Launch Templates console at [https://console.aws.amazon.com/ec2/v2/home?#LaunchTemplates:sort=launchTemplateId](https://console.aws.amazon.com/ec2/v2/home?#LaunchTemplates:sort=launchTemplateId) and check out the new version of your launch template.

### 9\. Create an auto scaling group for the production environment

In the development environment, you didn't need an auto scaling group since you were just deploying to a single instance. In production, you'll want an auto scaling group so that you can scale your instances with it.

Amazon EC2 Auto Scaling helps you maintain application availability and allows you to dynamically scale your Amazon EC2 capacity up or down automatically according to conditions you define. You can use Amazon EC2 Auto Scaling for fleet management of EC2 instances to help maintain the health and availability of your fleet and ensure that you are running your desired number of Amazon EC2 instances. You can also use Amazon EC2 Auto Scaling for dynamic scaling of EC2 instances in order to automatically increase the number of Amazon EC2 instances during demand spikes to maintain performance and decrease capacity during lulls to reduce costs. Amazon EC2 Auto Scaling is well suited both to applications that have stable demand patterns or that experience hourly, daily, or weekly variability in usage.

1. Edit **asg.json** update the values of **%TargetGroupArn%** from the previous steps.

1. Update the values of **%publicSubnet1%** and **%publicSubnet2%** from the CloudFormat stack outputs.

1. Save the file and create the auto scaling group:

	```
	aws autoscaling create-auto-scaling-group --cli-input-json file://asg.json
	```
	
1. Browse to the Auto Scaling console at [https://console.aws.amazon.com/ec2/autoscaling/home#AutoScalingGroups:view=details](https://console.aws.amazon.com/ec2/autoscaling/home#AutoScalingGroups:view=details) and check out your newly created auto scaling group. Take a look at the instances it has deployed.

### 10\. Deploy the application with CodeDeploy in the production environment

You will now deploy a production environment of Koel to the EC2 instances launched by the auto scaling group.

1. From the **prod** directory, first clone the Koel GitHub repo:

	```
	git clone https://github.com/phanan/koel.git
	
	cd koel && git checkout v3.7.2
	```
	
1. Next, copy the CodeDeploy configs into the root level of the koel application directory:

	```
	cp -avr ../codedeploy/* .
	```

1. For the production environment, you'll need to modify the deployment scripts in order to implement using the RDS database instance and the EFS file system. First edit **scripts/configure_db.sh**. Replace **%endpoint%** with the **Endpoint** of the database instance (e.g. **runningamazonec2workloadsatscale.ckhifpaueqm7.us-east-1.rds.amazonaws.com**
). Save the file.

1. Edit **scripts/start_services.sh** and replace **%fileSystem%** with the value in the CloudFormation stack outputs. Save the file.

1. After reviewing and getting comfortable with the CodeDeploy configs, go ahead and create the CodeDeploy application:

	```
	aws deploy create-application --application-name koelAppProd
	```

1. Browse to the AWS CodeDeploy console at [https://console.aws.amazon.com/codesuite/codedeploy/applications](https://console.aws.amazon.com/codesuite/codedeploy/applications) to check out your newly created application.
	
1. Next, push the application to the CodeDeploy S3 bucket. Be sure to replace **%codeDeployBucket%** with the value in the CloudFormation stack outputs:

	```
	aws deploy push --application-name koelAppDev --s3-location s3://%codeDeployBucket%/koelAppProd.zip --no-ignore-hidden-files
	```

1. Browse to the S3 console at [https://s3.console.aws.amazon.com/s3/home](https://s3.console.aws.amazon.com/s3/home) to check out your newly created application bundle in the 

1. Create the CodeDeploy deployment group by editing **deployment-group.json** and replacing the value of **%codeDeployServiceRole%** from the CloudFormation stack outputs, and then running:

	```
	cd ..
	
	aws deploy create-deployment-group --cli-input-json file://deployment-group.json
	```
	
	>Notice this time CodeDeploy is deploying to the auto scaling group instead of filtering by EC2 instance tags.

1. Browse to the AWS CodeDeploy console at [https://console.aws.amazon.com/codesuite/codedeploy/applications](https://console.aws.amazon.com/codesuite/codedeploy/applications) to check out your newly created deployment group.

1. Finally, deploy the application by editing **deployment.json** and replacing the value of **%codeDeployBucket%** from the CloudFormation stack outputs, and then running:

	```
	aws deploy create-deployment --cli-input-json file://deployment.json
	```
	
1. Browse to the AWS CodeDeploy console at [https://console.aws.amazon.com/codesuite/codedeploy/deployments](https://console.aws.amazon.com/codesuite/codedeploy/deployments) to monitor your application deployment.

1. Once the deploy is complete, browse to the public DNS of the load balancer (e.g. http://runningAmazonEC2WorkloadsAtScale-115077449.us-east-1.elb.amazonaws.com) and login. The default email address is **admin@example.com** and default password is **admin-pass**.

1. Find some mp3s on the interwebs and upload them to **/var/www/media** on the dev instance. *****THIS STEP NEEDS MORE DETAILS*****

1. Under **MANAGE**, click on **Settings**. Click on **Scan**. Play around and enjoy some tunes on your music service.

### 11\. Scale the application with a scheduled scaling action in the production environment

Scaling based on a schedule allows you to scale your application in response to predictable load changes. For example, every week the traffic to your web application starts to increase on Wednesday, remains high on Thursday, and starts to decrease on Friday. You can plan your scaling activities based on the predictable traffic patterns of your web application.

To configure your Auto Scaling group to scale based on a schedule, you create a scheduled action, which tells Amazon EC2 Auto Scaling to perform a scaling action at specified times. To create a scheduled scaling action, you specify the start time when the scaling action should take effect, and the new minimum, maximum, and desired sizes for the scaling action. At the specified time, Amazon EC2 Auto Scaling updates the group with the values for minimum, maximum, and desired size specified by the scaling action.

1. Edit **asg-scheduled-scaling.json** and replace **%StartTime%** with a UTC timestamp in about 10 minutes from now. For example: **2018-11-11T12:20:00**. You can use this [site](https://timestampgenerator.com/) to help. Look for the **Atom** format. Save the file.

1. Schedule the scaling action:

	```
	aws autoscaling put-scheduled-update-group-action --cli-input-json file://asg-scheduled-scaling.json
	```

1. Browse to the Auto Scaling console at [https://console.aws.amazon.com/ec2/autoscaling/home#AutoScalingGroups:view=details](https://console.aws.amazon.com/ec2/autoscaling/home#AutoScalingGroups:view=details) and check out your newly created scheduled scaling action. Wait for the time you chose, and take a look at the instances it has deployed.

1. Browse to the AWS CodeDeploy console at [https://console.aws.amazon.com/codesuite/codedeploy/deployments](https://console.aws.amazon.com/codesuite/codedeploy/deployments) to monitor your application deployment. Notice that CodeDeploy will automatically deploy the application to new instances launched by the auto scaling group.

### 12\. Dynamically scale the application with an automatic scaling policy in the production environment

When you configure dynamic scaling, you must define how to scale in response to changing demand. For example, you have a web application that currently runs on two instances and you do not want the CPU utilization of the Auto Scaling group to exceed 70 percent. You can configure your Auto Scaling group to scale automatically to meet this need. The policy type determines how the scaling action is performed.

Target tracking scaling policies simplify how you configure dynamic scaling. You select a predefined metric or configure a customized metric, and set a target value. Amazon EC2 Auto Scaling creates and manages the CloudWatch alarms that trigger the scaling policy and calculates the scaling adjustment based on the metric and the target value. The scaling policy adds or removes capacity as required to keep the metric at, or close to, the specified target value. In addition to keeping the metric close to the target value, a target tracking scaling policy also adjusts to the fluctuations in the metric due to a fluctuating load pattern and minimizes rapid fluctuations in the capacity of the Auto Scaling group.

1. Review **asg-automatic-scaling.json** to understand the options. There are no changes to be made. Then go ahead and apply the scaling policy:

	```
	aws autoscaling put-scaling-policy --cli-input-json file://asg-automatic-scaling.json
	```

1. Browse to the Auto Scaling console at [https://console.aws.amazon.com/ec2/autoscaling/home#AutoScalingGroups:view=details](https://console.aws.amazon.com/ec2/autoscaling/home#AutoScalingGroups:view=details) and check out your newly created scaling policy. Notice that in a few minutes, it will begin to scale down the instances that were previously scaled up by the scheduled scaling action in order to satisfy the target tracking metrics defined in the automatic scaling policy.

### 12\. Stress the application with AWS Systems Manager to trigger the automatic scaling policy in the production environment

AWS Systems Manager provides you safe, secure remote management of your instances at scale without logging into your servers, replacing the need for bastion hosts, SSH, or remote PowerShell. It provides a simple way of automating common administrative tasks across groups of instances such as registry edits, user management, and software and patch installations. Through integration with AWS Identity and Access Management (IAM), you can apply granular permissions to control the actions users can perform on instances. All actions taken with Systems Manager are recorded by AWS CloudTrail, allowing you to audit changes throughout your environment.

You will now emulate CPU stress on the instances in your automatic scaling group by issuing a remote command to each instance.

1. Review **ssm-stress.json** to understand the options. There are no changes to be made. Then go ahead and send the command:

	```
	aws ssm send-command --cli-input-json file://ssm-stress.json
	```

1. Browse to the AWS Systems Manager console at [https://console.aws.amazon.com/systems-manager/run-command/executing-commands](https://console.aws.amazon.com/systems-manager/run-command/executing-commands) to monitor the status of your run  commands.

1. Browse to the CloudWatch console at [https://console.aws.amazon.com/cloudwatch/home?#alarm:alarmFilter=ANY](https://console.aws.amazon.com/cloudwatch/home?#alarm:alarmFilter=ANY) to monitor the status of your alarms configured by the target tracking policy.

1. Browse to the Auto Scaling console at [https://console.aws.amazon.com/ec2/autoscaling/home#AutoScalingGroups:view=details](https://console.aws.amazon.com/ec2/autoscaling/home#AutoScalingGroups:view=details) and watch the activity history. Notice that in a few minutes, it will begin to scale up the instances according to the CloudWatch alarms the target tracking policy has configured for you.

1. Browse to the AWS CodeDeploy console at [https://console.aws.amazon.com/codesuite/codedeploy/deployments](https://console.aws.amazon.com/codesuite/codedeploy/deployments) to monitor your application deployment. Notice that CodeDeploy will automatically deploy the application to new instances launched by the auto scaling group.

* * *

## Finished!  
Congratulations on completing the workshop...*or at least giving it a good go*!  This is the workshop's permananent home, so feel free to revisit as often as you'd like.  In typical Amazon fashion, we'll be listening to your feedback and iterating to make it better.  If you have feedback, we're all ears!  Make sure you clean up after the workshop, so you don't have any unexpected charges on your next monthly bill.  

## Workshop Cleanup

1. Working backwards, delete all manually created resources.
3. Delete the CloudFormation stack launched at the beginning of the workshop.

## Appendix  

### Resources
Here are additional resources to learn more about Amazon EC2 Spot Instances.  

* [Amazon EC2 Spot Instances](https://aws.amazon.com/ec2/spot)
* [Amazon EC2 Spot Labs GitHub Repo](https://github.com/awslabs/ec2-spot-labs/)
* [Amazon EC2 Spot Fleet Jenkins Plugin](https://wiki.jenkins.io/display/JENKINS/Amazon+EC2+Fleet+Plugin)

### Articles
* [Taking Advantage of Amazon EC2 Spot Instance Interruption Notices](https://aws.amazon.com/blogs/compute/taking-advantage-of-amazon-ec2-spot-instance-interruption-notices/)
* [Powering Your Amazon ECS Clusters with Spot Fleet](https://aws.amazon.com/blogs/compute/powering-your-amazon-ecs-clusters-with-spot-fleet/)



