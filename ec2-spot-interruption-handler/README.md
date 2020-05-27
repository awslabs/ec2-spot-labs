# Spot Instance Interruption Handler

## Introduction
[Amazon EC2 Spot instances](https://aws.amazon.com/ec2/spot/) are spare EC2 capacity offered with an up to 90% discount compared to On-Demand pricing with the only consideration that they can be reclaimed with a two-minute warning if EC2 needs the capacity back. This two minutes warning is provided via the local EC2 metadata endpoint of each instance type (http://169.254.169.254/latest/meta-data/spot/instance-action) and via a an (optional) [Amazon EventBridge event](https://docs.aws.amazon.com/eventbridge/latest/userguide/create-eventbridge-rule.html), which can trigger a set of actions to gracefully handle the interruption.

## Handling Spot Instance Interruptions

This is a sample solution that deploys an Amazon EventBridge rule that catches Spot Instance Interruptions and triggers an AWS Lambda function to react to it. The handler takes actions when the instance that is going to be interrupted is part of an Auto Scaling group or a Spot Fleet and has a tag with Key: *SpotInterruptionHandler/enabled* and Value: *true*.

If the instance belongs to an Auto Scaling group, the function calls the Auto Scaling API to [detach](https://docs.aws.amazon.com/autoscaling/ec2/APIReference/API_DetachInstances.html) the instance from the Auto Scaling group. If the group has a Load Balancer configured, detaching the instance will put it in draining state to stop receiving new requests and allow time for in-flight requests to complete (default settings for ALB is 300 seconds, but it's recommended to adjust deregistration delay to 90 seconds or lower for Spot instances; see docs [here](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/load-balancer-target-groups.html#deregistration-delay)); as well as request Auto Scaling to attempt to launch a replacement instance based on your instance type selection and allocation strategy. 

Optionally, you can also configure a set of commands to be executed on your to-be-interrupted instance using AWS Systems Manager [Run Command](https://docs.aws.amazon.com/systems-manager/latest/userguide/execute-remote-commands.html); like gracefully stopping your application, deregister agents... In order to use this feature, your instances need to run the [AWS Systems Manager agent](https://docs.aws.amazon.com/systems-manager/latest/userguide/ssm-agent.html) (that comes pre-installed on Amazon Linux 2) and have an IAM Instance Profile with permissions to access the Systems manager API. You can find more configuration details [here](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-setting-up.html).

![Architecture](/ec2-spot-interruption-handler/images/architecture.png)

You can set up commands you want to execute when your Spot Instances on a specific Auto Scaling group or Spot Fleet are interrupted by creating a parameter within AWS Systems Manager [Parameter Store](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-parameter-store.html) with the commands you want to run. The Lambda function checks if a Parameter exists for the Auto Scaling group that the instance belongs to, if it exists, it will then call RunCommand referencing the parameter, otherwise the function finishes here. With default settings, the parameter name needs to be */spot-instance-interruption-handler/run_commands/\<auto-scaling-group-name\>* or */spot-instance-interruption-handler/run_commands/\<spot-fleet-id\>*.

You can delay the execution of termination commands to x seconds before the Spot instance interruption if, for example, you're allowing time for in-flight http requests to complete before you gracefully stop your application using the wait_x_seconds_before_interruption.sh bash script (it defaults to 30 seconds before interruption, but you can pass your desired time as parameter. It also requires [jq](https://stedolan.github.io/jq/) installed on the instance). Below you can find an example list of commands that will execute "echo executing termination commands" 60 seconds before the instance is going to be interrupted.

```bash
curl -s -o /tmp/wait_x_seconds_before_interruption.sh "https://raw.githubusercontent.com/awslabs/ec2-spot-labs/master/ec2-spot-interruption-handler/wait_x_seconds_before_interruption.sh"; chmod u+x /tmp/wait_x_seconds_before_interruption.sh; /tmp/wait_x_seconds_before_interruption.sh 60; echo "executing termination commands"
```

You can find an example Parameter for an Auto Scaling group named **SampleWebApp-AutoScalingGroup-1CRZJOLJHNXBI** on the image below:

![Parameter Store Example](/ec2-spot-interruption-handler/images/ParameterStore.png)

The Lambda function execution and the output of your commands is logged on Amazon CloudWatch Logs on the /aws/lambda/SpotInterruptionHandler and /aws/ssm/AWS-RunShellScript log groups respectively.

## Deploying the solution

### Deploy via Serverless Application Repository
Search for ec2-spot-interruption-handler in the Serverless Application Repository and follow the instructions to deploy. (Make sure you've checked the box labeled: Show apps that create custom IAM roles or resource policies)

If needed, you can modify the following parameters:
 - **SSMParameterPrefix:** The prefix of your Systems Manager Parameters where you will configure the commands you will run on the different ASGs. This defaults to /spot-instance-interruption-handler/run_commands/. If you leave the default settings, your parameters will need to be named */spot-instance-interruption-handler/run_commands/ \<auto-scaling-group-name\>*
 - **EnableRunCommandOutputLogging:** Enable logging to CloudWatch logs of the output of RunCommand (by default is set to *True*, you can disable it setting this to *False*)

### Deployment (Local)

#### Requirements

Note: For easiest deployment, create a Cloud9 instance and use the provided environment to deploy the function.

* AWS CLI already configured with Administrator permission
* [Python 3 installed](https://www.python.org/downloads/)
* [Docker installed](https://www.docker.com/community-edition)
* [SAM CLI installed](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)

#### Deployment Steps

Once you've installed the requirements listed above, open a terminal session as you'll need to run through a few commands to deploy the solution.

Firstly, we need a `S3 bucket` where we can upload our Lambda functions packaged as ZIP before we deploy anything - If you don't have a S3 bucket to store code artifacts then this is a good time to create one:

```bash
aws s3 mb s3://BUCKET_NAME
```
Next, clone the ec2-spot-labs repository to your local workstation or to your Cloud9 environment.

```
git clone https://github.com/awslabs/ec2-spot-labs.git
```

Next, change directories to the root directory for this example solution.

```
cd ec2-spot-labs/ec2-spot-interruption-handler
```

Next, run the following command to build the Lambda function:

```bash
sam build --use-container
```

Next, run the following command to package our Lambda function to S3:

```bash
sam package \
    --output-template-file packaged.yaml \
    --s3-bucket REPLACE_THIS_WITH_YOUR_S3_BUCKET_NAME
```

Next, the following command will create a Cloudformation Stack and deploy your SAM resources.

```bash
sam deploy \
    --template-file packaged.yaml \
    --stack-name ec2-spot-interruption-handler \
    --capabilities CAPABILITY_IAM \
```

If you want to configure a custom prefix for your AWS Systems Manager parameters or disable Systems Manager Run Command logging to Cloudwatch logs you can override defaults:


```bash
sam deploy \
    --template-file packaged.yaml \
    --stack-name ec2-spot-interruption-handler \
    --capabilities CAPABILITY_IAM \
    --parameter-overrides \
    SSMParameterPrefix=REPLACE_THIS_WITH_THE_NAME_YOU_WANT \
    EnableRunCommandOutputLogging=REPLACE_THIS_WITH_NUMBER_OF_DAYS_TO_RETAIN_LOGS  
```

## Costs of the solution

- Amazon EventBridge events for AWS service events are free of charge. Pricing details can be found [here](https://aws.amazon.com/eventbridge/pricing/)
- If you already use all the monthly free tier that AWS Lambda provides, Lambda pricing applies. Otherwise, the usage of this will be covered by the free tier. More info [here](https://aws.amazon.com/lambda/pricing/)
- AWS Systems Manager Run Command doesn't incur additional charges (limits apply). Parameter Store has also a Standard tier that doesn't incur charges. Pricing details can be found [here](https://aws.amazon.com/systems-manager/pricing/)
- AWS Lambda and Run Command log its output to CloudWatch logs. You can find pricing for CloudWatch Logs [here](https://aws.amazon.com/cloudwatch/pricing/)