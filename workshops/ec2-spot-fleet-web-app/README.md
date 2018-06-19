# Amazon EC2 Spot Fleet web app: Workshop guide
  
  
## Overview:
[Amazon EC2 Spot Instances](https://aws.amazon.com/ec2/spot/) are spare compute capacity in the AWS cloud available to you at steep discounts compared to On-Demand prices. EC2 Spot enables you to optimize your costs on the AWS cloud and scale your application's throughput up to 10X for the same budget. By simply selecting Spot when launching EC2 instances, you can save up-to 90% on On-Demand prices.

This workshop is designed to get you familiar with EC2 Spot Instances by learning how to deploy a simple web app on an EC2 Spot Fleet behind a load balancer and enable automatic scaling to allow it to handle peak demand, as well as handle Spot Instance interruptions.

## Requirements:  
To complete this workshop, have the [AWS CLI](https://aws.amazon.com/cli/) installed and configured, and appropriate permissions to launch EC2 instances and launch CloudFormation stacks within your AWS account.

This workshop is self-paced. The instructions will use both the AWS CLI and AWS Management Console- feel free to use either or both as you are comfortable.

**IMPORTANT:**
*This workshop has been designed to run in the AWS Region us-east-1 (Virginia). Please make sure you are operating in this region for all steps.*

## Architecture

In this workshop, you will deploy the following:

* An Amazon Virtual Private Cloud (Amazon VPC) with subnets in two Availability Zones
* An Application Load Balancer with a listener and target group
* An Amazon CloudWatch Events rule
* An AWS Lambda function
* An Amazon Simple Notification Service (SNS) topic
* Associated IAM policies and roles for all of the above
* An Amazon EC2 Spot Fleet request diversified across both Availability Zones using a couple of recent Spot Fleet features: Elastic Load Balancing integration and Tagging Spot Fleet Instances

When any of the Spot Instances receives an interruption notice, Spot Fleet sends the event to CloudWatch Events. The CloudWatch Events rule then notifies both targets, the Lambda function and SNS topic. The Lambda function detaches the Spot Instance from the Application Load Balancer target group, taking advantage of a full two minutes of connection draining before the instance is interrupted. The SNS topic also receives a message, and is provided as an example for the reader to use as an exercise (***hint***: have it send you an email or an SMS message).

Here is a diagram of the resulting architecture:

![](images/interruption_notices_arch_diagram.jpg)

## Let's Begin!  

### Launch the CloudFormation stack

To save time on the initial setup, a CloudFormation template will be used to create the Amazon VPC with subnets in two Availability Zones, as well as the IAM policies and roles, and security groups.

1\. Go ahead and launch the CloudFormation stack. You can check it out from GitHub, or grab the template directly. I use the stack name “ec2-spot-fleet-web-app“, but feel free to use any name you like. Just remember to change it in the instructions.

`
$ git clone https://github.com/awslabs/ec2-spot-labs.git
`

`
$ aws cloudformation create-stack --stack-name ec2-spot-fleet-web-app --template-body file://ec2-spot-labs/workshops/ec2-spot-fleet-web-app/ec2-spot-fleet-web-app.yaml --capabilities CAPABILITY_IAM --region us-east-1
`

You should receive a StackId value in return, confirming the stack is launching.

	{
	  "StackId": "arn:aws:cloudformation:us-east-1:123456789012:stack/spot-fleet-web-app/083e7ad0-0ade-11e8-9e36-500c219ab02a"
	}

2\. Wait for the status of the CloudFormation stack to move to **CREATE_COMPLETE** before moving on to the next step. You will need to reference the Output values from the stack in the next steps.


### Deploy the load balancer

To deploy your load balancer and Spot Fleet in your AWS account, you will begin by signing in to the AWS Management Console with your user name and password. 

1\. Go to the EC2 console by choosing EC2 under “Compute.”

2\. Next, choose Load Balancers in the navigation pane. This page shows a list of load balancer types to choose from.

3\. Choose Create in the Application Load Balancer box. 

4\. Give your load balancer a name.

5\. You can leave the rest of the Basic Configuration and Listeners options as default for the purposes of this workshop.

6\. Under Availability Zones, you'll need to select the VPC created by the CloudFormation stack you launched in the previous step, and then select both Availability Zones for the load balancer to route traffic to. Best practices for both load balancing and Spot Fleet are to select at least two Availability Zones - ideally you should select as many as possible. Remember that you can specify only one subnet per Availability Zone.

7\. Once done, click on Next: Configure Security Settings.

*Since this is a demonstration, we will continue without configuring a secure listener. However, if this was a production load balancer, it is recommended to configure a secure listener if your traffic to the load balancer needs to be secure.*

8\. Go ahead and click on Next: Configure Security Groups. Choose **Select an existing security group**, then select both the **default** security group, and the security group created in the CloudFormation stack.

9\. Click on Next: Configure Routing.

10\. In the Configure Routing section, we'll configure a Target group. Your load balancer routes requests to the targets in this target group using the protocol and port that you specify, and performs health checks on the targets using these health check settings. Give your Target group a Name, and leave the rest of the options as default under Target group, Health checks, and Advanced health check settings.

11\. Click on Next: Register Targets. On the Register Targets section, we don't need to register any targets or instances at this point, because we will do this when we configure the EC2 Spot Fleet.

12\. Click on Next: Review.

13\. Here you can review your settings. Once you are done reviewing, click Create.

14\. You should get a return that your load balancer was successfully created. Click Close.

### Launch an EC2 Spot Fleet and associate the Load Balancing Target Group with it




1\. First, you'll need to select a [region](http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-regions-availability-zones.html). For this lab, you will need to choose either **Ohio** or **Oregon**. At the top right hand corner of the AWS Console, you'll see a **Support** dropdown. To the left of that is the region selection dropdown.

2\. Then you'll need to create an SSH key pair which will be used to login to the instances once provisioned.  Go to the EC2 Dashboard and click on **Key Pairs** in the left menu under Network & Security.  Click **Create Key Pair**, provide a name (can be anything, make it something memorable) when prompted, and click **Create**.  Once created, the private key in the form of .pem file will be automatically downloaded.  

If you're using linux or mac, change the permissions of the .pem file to be less open.  

<pre>$ chmod 400 <b><i>PRIVATE_KEY.PEM</i></b></pre>

If you're on windows you'll need to convert the .pem file to .ppk to work with putty.  Here is a link to instructions for the file conversion - [Connecting to Your Linux Instance from Windows Using PuTTY](http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/putty.html)

3\. For your convenience, we provide a CloudFormation template to stand up the core infrastructure.  

*Prior to launching a stack, be aware that a few of the resources launched need to be manually deleted when the workshop is over. When finished working, please review the "Workshop Cleanup" section to learn what manual teardown is required by you.*

Click on one of these CloudFormation templates that matches the region you created your keypair in to launch your stack:  

Region | Launch Template
------------ | -------------  
**Ohio** (us-east-2) | [![Launch ECS Deep Learning Stack into Ohio with CloudFormation](/images/deploy-to-aws.png)](https://console.aws.amazon.com/cloudformation/home?region=us-east-2#/stacks/new?stackName=ecs-deep-learning-stack&templateURL=https://s3.amazonaws.com/ecs-dl-workshop-us-east-2/ecs-deep-learning-workshop.yaml)  
**Oregon** (us-west-2) | [![Launch ECS Deep Learning Stack into Oregon with CloudFormation](/images/deploy-to-aws.png)](https://console.aws.amazon.com/cloudformation/home?region=us-west-2#/stacks/new?stackName=ecs-deep-learning-stack&templateURL=https://s3.amazonaws.com/ecs-dl-workshop-us-west-2/ecs-deep-learning-workshop.yaml)  

The template will automatically bring you to the CloudFormation Dashboard and start the stack creation process in the specified region.  The template sets up a VPC, IAM roles, S3 bucket, ECR container registry and an ECS cluster which is comprised of one EC2 Instance with the Docker daemon running.  The idea is to provide a contained environment, so as not to interfere with any other provisioned resources in your account.  In order to demonstrate cost optimization strategies, the EC2 Instance is an [EC2 Spot Instance](https://aws.amazon.com/ec2/spot/) deployed by [Spot Fleet](http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/spot-fleet.html).  If you are new to [CloudFormation](https://aws.amazon.com/cloudformation/), take the opportunity to review the [template](https://github.com/awslabs/ecs-deep-learning-workshop/blob/master/lab-1-setup/cfn-templates/ecs-deep-learning-workshop.yaml) during stack creation.

**IMPORTANT**  
*On the parameter selection page of launching your CloudFormation stack, make sure to choose the key pair that you created in step 1. If you don't see a key pair to select, check your region and try again.*
![CloudFormation PARAMETERS](/images/cf-params.png)

**Create the stack**  
After you've selected your ssh key pair, click **Next**. On the **Options** page, accept all defaults- you don't need to make any changes. Click **Next**. On the **Review** page, under **Capabilities** check the box next to **"I acknowledge that AWS CloudFormation might create IAM resources."** and click **Create**. Your CloudFormation stack is now being created.

**Checkpoint**  
Periodically check on the stack creation process in the CloudFormation Dashboard.  Your stack should show status **CREATE\_COMPLETE** in roughly 5-10 minutes.  In the Outputs tab, take note of the **ecrRepository** and **spotFleetName** values; you will need these in the next lab.     

![CloudFormation CREATION\_COMPLETE](/images/cf-complete.png)

Note that when your stack moves to a **CREATE\_COMPLETE** status, you won't necessarily see EC2 instances yet. If you don't, go to the EC2 console and click on **Spot Requests**. There you will see the pending or fulfilled spot requests. Once they are fulfilled, you will see your EC2 instances within the EC2 console.

If there was an error during the stack creation process, CloudFormation will rollback and terminate.  You can investigate and troubleshoot by looking in the Events tab.  Any errors encountered during stack creation will appear in the event log.      

### Lab 2 - Build an MXNet Docker Image:    
In this lab, you will build an MXNet Docker image using one of the ECS cluster instances which already comes bundled with Docker installed.  There are quite a few dependencies for MXNet, so for your convenience, we have provided a Dockerfile in the lab 2 folder to make sure nothing is missed.  You can review the [Dockerfile](https://github.com/awslabs/ecs-deep-learning-workshop/blob/master/lab-2-build/mxnet/Dockerfile) to see what's being installed.  Links to MXNet documentation can be found in the [Appendix](https://github.com/awslabs/ecs-deep-learning-workshop/#appendix) if you'd like to read more about it.  

1\. Go to the EC2 Dashboard in the Management Console and click on **Instances** in the left menu.  Select the EC2 instance created by the CloudFormation stack.  If your instances list is cluttered with other instances, apply a filter in the search bar using the tag key **aws:ec2spot:fleet-request-id** and choose the value that matches the **spotFleetName** from your CloudFormation Outputs.  

![EC2 Public DNS](/images/ec2-public-dns.png)

Once you've selected one of the provisioned EC2 instances, note the Public DNS Name and SSH into the instance.  

<pre>
$ ssh -i <b><i>PRIVATE_KEY.PEM</i></b> ec2-user@<b><i>EC2_PUBLIC_DNS_NAME</i></b>
</pre>

2\. Once logged into the EC2 instance, clone the workshop github repository so you can easily access the Dockerfile.  
<pre>$ git clone https://github.com/awslabs/ecs-deep-learning-workshop.git</pre>

3\. Navigate to the lab-2-build/mxnet/ folder to use as your working directory.  
<pre>$ cd ecs-deep-learning-workshop/lab-2-build/mxnet</pre>

4\. Build the Docker image using the provided Dockerfile.  A build argument is used to set the password for the Jupyter notebook login which is used in a later lab.  <b>Also, note the trailing period in the command below!!</b>

<pre>
$ docker build --build-arg PASSWORD=<b><i>INSERT_A_PASSWORD</i></b> -t mxnet .
</pre>

**IMPORTANT**  
*It is not recommended to use build-time variables for passing secrets like github keys, user credentials etc. Build-time variable values are visible to any user of the image with the docker history command. We have chosen to do it for this lab for simplicity's sake. There are various other methods for secrets management like using [DynamoDB with encryption](https://aws.amazon.com/blogs/developer/client-side-encryption-for-amazon-dynamodb/) or [S3 with encryption](https://aws.amazon.com/blogs/security/how-to-manage-secrets-for-amazon-ec2-container-service-based-applications-by-using-amazon-s3-and-docker/) for key storage and using [IAM Roles](http://docs.aws.amazon.com/AmazonECS/latest/developerguide/task-iam-roles.html) for granting access.  There are also third party tools such as [Hashicorp Vault](https://www.vaultproject.io/) for secrets management.*

This process will take about 10-15 minutes because MXNet is being compiled during the build process.  If you're new to Docker, you can take this opportunity to review the Dockerfile to understand what's going on or take a quick break to grab some coffee/tea.  

5\. Now that you've built your local Docker image, you'll need to tag and push the MXNet Docker image to ECR.  You'll reference this image when you deploy the container using ECS in the next lab.  Find your respository URI in the EC2 Container Service Dashboard; click on **Repositories** in the left menu and click on the repository name that matches the **ecrRepository** output from CloudFormation. The Repository URI will be listed at the top of the screen.  

![ECR URI](/images/ecr-uri.png)  

In your terminal window, tag and push the image to ECR:    
<pre>
$ docker tag mxnet:latest <b><i>AWS_ACCOUNT_ID</i></b>.dkr.ecr.<b><i>AWS_REGION</i></b>.amazonaws.com/<b><i>ECR_REPOSITORY</i></b>:latest   
$ docker push <b><i>AWS_ACCOUNT_ID</i></b>.dkr.ecr.<b><i>AWS_REGION</i></b>.amazonaws.com/<b><i>ECR_REPOSITORY</i></b>:latest  
</pre>

Following the example above, you would enter these commands:
<pre>
$ docker tag mxnet:latest 873896820536.dkr.ecr.us-east-2.amazonaws.com/ecs-w-ecrre-1vpw8bk5hr8s9:latest
$ docker push 873896820536.dkr.ecr.us-east-2.amazonaws.com/ecs-w-ecrre-1vpw8bk5hr8s9:latest
</pre>

You can copy and paste the Repository URI to make things simpler.

**Checkpoint**  
Note that you did not need to authenticate docker with ECR because the [Amazon ECR Credential Helper](https://github.com/awslabs/amazon-ecr-credential-helper) has been installed and configured for you on the EC2 instance.

At this point you should have a working MXNet Docker image stored in an ECR repository and ready to deploy with ECS.


### Lab 3 - Deploy the MXNet Container with ECS:    
Now that you have an MXNet image ready to go, the next step is to create a task definition. A task defintion specifies parameters and requirements used by ECS to run your container, e.g. the Docker image, cpu/memory resource requirements, host:container port mappings.  You'll notice that the parameters in the task definition closely match options passed to a Docker run command.  Task definitions are very flexible and can be used to deploy multiple containers that are linked together- for example, an application server and database.  In this workshop, we will focus on deploying a single container.         

1\. Open the EC2 Container Service dashboard, click on **Task Definitions** in the left menu, and click **Create new Task Definition**.    

*Note: You'll notice there's a task definition already there in the list.  Ignore this until you reach lab 5.*  

2\. First, name your task definition, e.g. "mxnet".  If you happen to create a task definition that is a duplicate of an existing task definition, ECS will create a new revision, incrementing the version number automatically.  

3\. Next, click on **Add container** and complete the fields in the Add container window; for this lab, you will only need to complete the Standard fields.  

Provide a name for your container, e.g. "mxnet".  Note: This name is functionally equivalent to the "--name" option of the Docker run command and can also be used for container linking.  

The image field is the container image that you will be deploying.  The format is equivalent to the *registry/repository:tag* format used in lab 2, step 6, i.e. ***AWS_ACCOUNT_ID***.dkr.ecr.***AWS_REGION***.amazonaws.com/***ECR_REPOSITORY***:latest.  

Finallly, set the Memory Limits to be a Soft Limit of "2048" and map the host port 80 to the container port 8888.  Port 8888 is the listening port for the Jupter notebook configuration, and we map it to port 80 to reduce running into issues with proxies or firewalls blocking port 8888 during the workshop.  You can leave all other fields as default.  Click **Add** to save this configuration and add it to the task defintion.  Click **Create** to complete the task definition creation step.         

![Task Definition](/images/task-def.png)  

4\. Now that you have a task definition created, you can have ECS deploy an MXNet container to your EC2 cluster using the Run Task option.  In the **Actions** dropdown menu, select **Run Task**.  

Choose your ECS Cluster from the dropdown menu.  If you have multiple ECS Clusters in the list, you can find your workshop cluster by referring to the **ecsClusterName** value from the CloudFormation stack Outputs tab.  You can leave all other fields as default.  Keep number of tasks set to 1 and click **Run Task**.  

ECS is now running your MXNet container on an ECS cluster instance with available resources.  If you run multiple tasks, ECS will balance out the tasks across the cluster, so one cluster instance doesn't have a disproportionate number of tasks.  

5\. On the Cluster detail page, you'll see a Tasks tab towards the bottom of the page.  Notice your new task starts in the Pending state.  Click on the refresh button after about 30 seconds to refresh the contents of that tab, repeating the refresh until it is in the Running state. Once the task is in the Running state, you can test accessing the Jupyter notebook.  In addition to the displaying the state of the task, this tab also identifies which container instance the task is running on.  Click on the Container Instance and you'll see the Public DNS of the EC2 instance on the next page.   

![Run Task](/images/task-run.png)  

6\. Open a new web browser tab and load the public DNS name to test Jupyter loads properly - http://***EC2_PUBLIC_DNS_NAME***.

7\. You should be prompted for the password you passed in earlier as a build-arg. Enter the password and you should be able to log in.

![Log In](/images/jupyter-login.png)  

### Lab 4 - Image Classification with MXNet:   
Now that you have an MXNet container built and deployed with ECS, you can try out an image classification example provided by MXNet to make sure the framework is working properly.  There are two examples you can run through, one for training a model and one for generating a prediction.            

#### Training:    
The first step is to train a model that you can then generate predictions off of later. In this lab, you will use the MNIST database. The MNIST database is a database consisting of handwritten digits very commonly used for training various image processing systems. In the MXNet example for training an MNIST model, there is a python file that runs the training. You will SSH into the same host that already has Jupyter running that you found in step 5 of lab 3, connect to a specific container, and finally run the training command.

First, SSH into the instance:
<pre>
$ ssh -i <b><i>PRIVATE_KEY.PEM</i></b> ec2-user@<b><i>EC2_PUBLIC_DNS_NAME</i></b>
</pre>

Once logged in, find the container to connect to by running:
<pre>
$ docker ps
</pre>

On the left hand side, you'll find two containers that are running. One for our mxnet container, and one for the amazon-ecs-agent. Note down the CONTAINER_ID of the mxnet image so we can open a bash shell like this:

<pre>
$ docker exec -it <b><i>CONTAINER_ID</i></b> /bin/bash
</pre>

Now that you're in the container, you can feel free to navigate around. It should look very similar compared to what you saw in lab 2. Once you're ready, navigate to /root/ecs-deep-learning-workshop/mxnet/example/image-classification/ and run train_mnist.py

<pre>
$ cd /root/ecs-deep-learning-workshop/mxnet/example/image-classification/
$ python train_mnist.py
</pre>

You will start to see output right away. It will look like:
<pre>
INFO:root:Start training with [cpu(0)]
INFO:root:Epoch[0] Batch [100]	Speed: 13736.09 samples/sec	Train-accuracy=0.782969
INFO:root:Epoch[0] Batch [200]	Speed: 12799.08 samples/sec	Train-accuracy=0.910000
INFO:root:Epoch[0] Batch [300]	Speed: 13594.84 samples/sec	Train-accuracy=0.926094
INFO:root:Epoch[0] Batch [400]	Speed: 13775.83 samples/sec	Train-accuracy=0.933594
INFO:root:Epoch[0] Batch [500]	Speed: 13732.46 samples/sec	Train-accuracy=0.937656
INFO:root:Epoch[0] Batch [600]	Speed: 13788.14 samples/sec	Train-accuracy=0.941719
INFO:root:Epoch[0] Batch [700]	Speed: 13735.79 samples/sec	Train-accuracy=0.937813
INFO:root:Epoch[0] Batch [800]	Speed: 13789.07 samples/sec	Train-accuracy=0.944531
INFO:root:Epoch[0] Batch [900]	Speed: 13754.83 samples/sec	Train-accuracy=0.953750
</pre>

As you should be able to tell, logging into a machine, then dropping into a shell onto a container isn't the best process to do all of this, and it's very manual. In the prediction section, we will show you a more interactive method of running commands.


#### Prediction:
Since training a model can be resource intensive and a lengthy process, you will run through an example that uses a pre-trained model built from the full [ImageNet](http://image-net.org/) dataset, which is a collection of over 10 million images with thousands of classes for those images.  This example is presented as a Juypter notebook, so you can interactively walk through the example.  

If you're new to Jupyter, it is essentially a web application that allows you to interactively step through blocks of written code.  The code can be edited by the user as needed or desired, and there is a play button that lets you step through the cells.  Cells that do not code have no effect, so you can hit play to pass through the cell.  
 
1\. Open a web browser and visit this URL to access the Jupyter notebook for the demo:

http://***EC2_PUBLIC_DNS_NAME***/notebooks/mxnet-notebooks/python/tutorials/predict_imagenet.ipynb

2\. Play through the cells to run through this example, which loads and prepares the pre-trained model as well as provide methods to load images into the model to predict its classification.  If you've never used Jupyter before, you're probably wonder how you know something is happening.  Cells with code are denoted on the left with "In [n]" where n is simply a cell number.  When you play a cell that requires processing time, the number will show an asterisk.  

**IMPORTANT**: In cell 2, the default context is to use gpu, but in the case of this workshop, we're using cpu resources so change the text "gpu" to "cpu".  Being able to switch between using cpu and gpu is a great feature of this library.  See the following screenshot which illustrates where to change from gpu to cpu; also highlighted in the screenshot is the play button which lets you run the cells.  While deep learning performance is better on gpu, you can make use of cpu resources in dev/test environments to keep costs down.  

![Jupyter Notebook - Prediction](/images/jupyter-notebook-predict.png)

3\. Once you've stepped through the two examples at the end of the notebook, try feeding arbitrary images to see how well the model performs.  Remember that Jupyter notebooks let you input your own code in a cell and run it, so feel free to experiment.    

### Lab 5 - Wrap Image Classification in an ECS Task:
At this point, you've run through training and prediction examples using the command line and using a Juypter notebook, respectively.  You can also create task definitions to execute these commands, log the outputs to both S3 and CloudWatch Logs, and terminate the container when the task has completed.  S3 will store a log file containing the outputs from each task run, and CloudWatch Logs will have a log group that continues to append outputs from each task run.  In this lab, you will create additional task definitions to accomplish this.  The steps should be familiar because you've done this in lab 3, only the configuration of the task definition will be slightly different. 

*Note: The task definition that was created by the CloudFormation template is an example of a prediction task that you can refer to for help if you get stuck.*  


#### Training task

1\. Open the EC2 Container Service dashboard, click on **Task Definitions** in the left menu, and click **Create new Task Definition**.    

2\. Name your task definition, e.g. "mxnet-train".  

3\. Click on **Add container** and complete the Standard fields in the Add container window.  Provide a name for your container, e.g. "mxnet-train".  The image field is the same container image that you deployed previously.  As a reminder, the format is equivalent to the *registry/repository:tag* format used in lab 2, step 6, i.e. ***AWS_ACCOUNT_ID***.dkr.ecr.***AWS_REGION***.amazonaws.com/***ECR_REPOSITORY***:latest.  

Set the memory to "1024".  Leave the port mapping blank because you will not be starting the Jupyter process, and instead running a command to perform the training.  

Scroll down to the **Advanced Container configuration** section, and in the **Entry point** field, type:  

<pre>
/bin/bash, -c
</pre>

In the **Command** field, type:  

<pre>
DATE=`date -Iseconds` && echo \\\"running train_mnist.py\\\" && cd /root/ecs-deep-learning-workshop/mxnet/example/image-classification/ && python train_mnist.py |& tee results && echo \\\"results being written to s3://$OUTPUTBUCKET/train_mnist.results.$HOSTNAME.$DATE.txt\\\" && aws s3 cp results s3://$OUTPUTBUCKET/train_mnist.results.$HOSTNAME.$DATE.txt && echo \\\"Task complete!\\\"
</pre>  

The command references an OUTPUTBUCKET environment variable, and you can set this in **Env variables**.  Set the key to be "OUTPUTBUCKET" and the value to be the S3 output bucket created by CloudFormation.  You can find the value of your S3 output bucket by going to the CloudFormation stack outputs tab, and used the value for **outputBucketName**.   Set "AWS_DEFAULT_REGION" to be the value of **awsRegionName** from the CloudFormation stack outputs tab.

![Advanced Configuration - Environment](/images/adv-config-env-train.png)  

Next you'll configure logging to CloudWatch Logs.  Scroll down to the **Log configuration**, select **awslogs** from the *Log driver* dropdown menu.  For *Log options*, set the **awslogs-group** to be the value of **cloudWatchLogsGroupName** from the CloudFormation stack outputs tab.  And type in the region you're currently using, e.g. Ohio would be us-east-2, Oregon would be us-west-2.  Leave the **awslogs-stream-prefix** blank.  

![Advanced Configuration - Log configuration](/images/adv-config-log-train.png)  
  
If you are using GPU instances, you will need to check the box for **Privileged** in the **Security** section.  Since we're using CPU instances, leave the box unchecked.          

Click **Add** to save this configuration and add it to the task defintion.  Click **Create** to complete the task defintion creation step.         

4\. Now you're ready to test your task definition.  Select **Run Task** from the **Actions** drop down.  Refresh the task list to confirm the task enters the Running state.  

5\. The task outputs logs to CloudWatch Logs as well as S3.  Open the **CloudWatch** dashboard, and click on **Logs** in the left menu.  Click on the log group, and then click on the log stream that was created.  You should see log output from the task run; since the training task takes some time to complete, you'll see the log output continue to stream in.  Once the task has completed and stopped, check your S3 output bucket, and you should see a log file has been written.  Download the log file and check the content.

![CloudWatch Logs](/images/cw-logs.png)  


#### Prediction task

1\. Return to the **Task Definitions** page, and click **Create new Task Definition**.    

2\. Name your task definition, e.g. "mxnet-predict".  

3\. Click on **Add container** and complete the Standard fields in the Add container window.  Provide a name for your container, e.g. "mxnet-predict".  The image field is the same container image that you deployed previously.  As a reminder, the format is equivalent to the *registry/repository:tag* format used in lab 2, step 6, i.e. ***AWS_ACCOUNT_ID***.dkr.ecr.***AWS_REGION***.amazonaws.com/***ECR_REPOSITORY***:latest.  

Set the memory to "1024".  Leave the port mapping blank because you will not be starting the Jupyter process, and instead running a command to perform the training.  

Scroll down to the **Advanced Container configuration** section, and in the **Entry point** field, type:  

<pre>
/bin/bash, -c
</pre>

In the **Command** field, type:  

<pre>
DATE=`date -Iseconds` && echo \"running predict_imagenet.py $IMAGEURL\" && /usr/local/bin/predict_imagenet.py $IMAGEURL |& tee results && echo \"results being written to s3://$OUTPUTBUCKET/predict_imagenet.results.$HOSTNAME.$DATE.txt\" && aws s3 cp results s3://$OUTPUTBUCKET/predict_imagenet.results.$HOSTNAME.$DATE.txt && echo \"Task complete!\"
</pre>  

Similar to the training task, configure the **Env variables** used by the command.  Set "OUTPUTBUCKET" to be the value of **outputBucketName** from the CloudFormation stack outputs tab.  Set "IMAGEURL" to be a URL to an image to be classified.  This can be a URL to any image, but make sure it's an absolute path to an image file and not one that is dynamically generated.  Set "AWS_DEFAULT_REGION" to be the value of **awsRegionName** from the CloudFormation stack outputs tab.    

![Advanced Configuration - Environment](/images/adv-config-env-predict.png)  

Configure the **Log configuration** section as you did for the training task.  Select **awslogs** from the *Log driver* dropdown menu.  For *Log options*, set the **awslogs-group** to be the value of **cloudWatchLogsGroupName** from the CloudFormation stack outputs tab.  And type in the region you're currently using, e.g. Ohio would be us-east-2, Oregon would be us-west-2.  Leave the **awslogs-stream-prefix** blank.    
  
If you are using GPU instances, you will need to check the box for **Privileged** in the **Security** section.  Since we're using CPU instances, leave the box unchecked.          

Click **Add** to save this configuration and add it to the task defintion.  Click **Create** to complete the task defintion creation step. 

4\. Run the predict task and check both CloudWatch Logs and the S3 output bucket for related log output.  


### Extra Credit Challenges:
* An S3 input bucket was created by the CloudFormation template.  Try uploading images to S3 and running the prediction task against those images.
* Modify the Dockerfile to enable a password in the Jupyter web interface.
* Trigger a lambda function when an image is uploaded to the S3 input bucket and have that lambda function call the prediction task.  

* * *

## Finished!  
Congratulations on completing the lab...*or at least giving it a good go*!  This is the workshop's permananent home, so feel free to revisit as often as you'd like.  In typical Amazon fashion, we'll be listening to your feedback and iterating to make it better.  If you have feedback, we're all ears!  Make sure you clean up after the workshop, so you don't have any unexpected charges on your next monthly bill.  

* * *

## Workshop Cleanup:

1. Delete any manually created resources throughout the labs.
2. Delete any data files stored on S3 and container images stored in ECR.
3. Delete the CloudFormation stack launched at the beginning of the workshop.

* * *

## Appendix:  

### Estimated Costs:    
The estimated cost for running this 2.5 hour workshop will be less than $5.

### Learning Resources:  
Here are additional resources to learn more about AWS, Docker, MXNet.  

* [Amazon Web Services](https://aws.amazon.com/)  
* [A Cloud Guru - online self-paced labs](https://acloud.guru/courses)  
* [Docker documentation](https://docs.docker.com/)  
* [MXNet](http://mxnet.io/)  
* [MXNet Examples](http://mxnet.io/tutorials/index.html)  

#### Articles:  
* [Powering ECS Clusters with Spot Fleet](https://aws.amazon.com/blogs/compute/powering-your-amazon-ecs-clusters-with-spot-fleet/)  
* [Distributed Deep Learning Made Easy](https://aws.amazon.com/blogs/compute/distributed-deep-learning-made-easy/)



