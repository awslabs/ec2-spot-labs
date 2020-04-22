# Spot Instance Interruption Handler

## Introduction
[Amazon EC2 Spot instances](https://aws.amazon.com/ec2/spot/) are spare EC2 capacity offered with an up to 90% discount compared to On-Demand pricing with the only consideration that they can be reclaimed with a two-minute warning if EC2 needs the capacity back. This two minutes warning is provided via the local EC2 metadata endpoint of each instance type (http://169.254.169.254/latest/meta-data/spot/instance-action) and via a an (optional) [Amazon EventBridge event](https://docs.aws.amazon.com/eventbridge/latest/userguide/create-eventbridge-rule.html), which can trigger a set of actions to gracefully handle the interruption.

## Handling Spot Instance Interruptions

This is a sample solution that provides a CloudFormation template that deploys an Amazon EventBridge rule that catches Spot Instance Interruptions and triggers an AWS Lambda function to react to it. The handler takes actions when the instance that is going to be interrupted is part of an Auto Scaling group, which is the best way to launch and manage Spot instances while adhering to best practices by [combining multiple instance types and purchase options within an Auto Scaling group](https://docs.aws.amazon.com/autoscaling/ec2/userguide/asg-purchase-options.html). 

When receiving an interruption notice, the function calls the Auto Scaling API to [detach](https://docs.aws.amazon.com/autoscaling/ec2/APIReference/API_DetachInstances.html) the instance from the Auto Scaling group. If the group has a Load Balancer configured, detaching the instance will put it in draining state to stop receiving new requests and allow time for in-flight requests to complete (default settings for ALB is 300 seconds, but it's recommended to adjust deregistration delay to 90 seconds or lower for Spot instances; see docs [here](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/load-balancer-target-groups.html#deregistration-delay)); as well as request Auto Scaling to attempt to launch a replacement instance based on your instance type selection and allocation strategy. 

Optionally, you can also configure a set of commands to be executed on your to-be-interrupted instance using AWS Systems Manager [Run Command](https://docs.aws.amazon.com/systems-manager/latest/userguide/execute-remote-commands.html); like gracefully stopping your application, deregister agents... In order to use this feature, your instances need to run the [AWS Systems Manager agent](https://docs.aws.amazon.com/systems-manager/latest/userguide/ssm-agent.html) (that comes pre-installed on Amazon Linux 2) and have an IAM Instance Profile with permissions to access the Systems manager API. You can find more configuration details [here](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-setting-up.html).

You can set up commands you want to execute when your Spot Instances on a specific Auto Scaling group are interrupted by creating a parameter within AWS Systems Manager [Parameter Store](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-parameter-store.html) with the commands you want to run. The Lambda function checks if a Parameter exists for the Auto Scaling group that the instance belongs to, if it exists, it will then call RunCommand referencing the parameter, otherwise the function finishes here. With default settings, the parameter name needs to be */spot-instance-interruption-handler/run_commands/\<auto-scaling-group-name\>* .

![Architecture](/ec2-spot-interruption-handler/images/architecture.png)

You can delay the execution of termination commands to x seconds before the Spot instance interruption if, for example, you're allowing time for in-flight http requests to complete before you graceuflly stop your application using the wait_x_seconds_before_interruption.sh bash script (it defaults to 30 seconds before interruption, but you can pass your desired time as parameter. It also requires [jq](https://stedolan.github.io/jq/) installed on the instance). Below you can find an example list of commands that will execute "echo executing termination commands" 60 seconds before the instance is going to be interrupted.

```bash
curl -s -o /tmp/wait_x_seconds_before_interruption.sh "https://raw.githubusercontent.com/awslabs/ec2-spot-labs/master/ec2-spot-interruption-handler/wait_x_seconds_before_interruption.sh"; chmod u+x /tmp/wait_x_seconds_before_interruption.sh; /tmp/wait_x_seconds_before_interruption.sh 60; echo "executing termination commands"
```

Both the Lambda function execution and the output of your commands is logged on Amazon CloudWatch Logs on the /aws/lambda/SpotInterruptionHandler and /aws/ssm/AWS-RunShellScript log groups respectively.

## Setup instructions

To set up the Spot interruption handler, follow these steps:

1. Download the index.py file to your local computer and zip it. 
1. Upload the zipped Lambda function to an Amazon S3 Bucket in the region you want to deploy the Spot Interruption Handler.
1. Deploy the cloudformation.yml template and fill in the parameters:
    - **LambdaFunctionS3Bucket:** The name of the S3 bucket where you have uploaded the zipped function.
    - **LambdaFunctionS3Key:** The S3 key where you have uploaded the zipped function
    - **ASGSSMParameterPrefix:** The prefix of your Systems Manager Parameters where you will configure the commands you will run on the different ASGs. This defaults to /spot-instance-interruption-handler/run_commands/. If you leave the default settings, your parameters will need to be named */spot-instance-interruption-handler/run_commands/  \<auto-scaling-group-name\>*
    - **EnableRunCommandOutputLogging:** Enable logging to CloudWatch logs of the output of RunCommand (by default is set to *True*, you can disable it setting this to *False*)

Once the CloudFormation template is deployed, the Spot Interruption Handler will be triggered when any Spot instance in your account within the AWS region it's deployed gets an Interruption Notice. If the instance that is going to be interrupted is part of an AutoScaling group, it will put the to-be-interrupted instance in draining state and request Auto Scaling to attempt to launch replacement capacity using the configured Spot Instance types and allocation strategy. If there are no Parameters configured in AWS Systems Manager matching your *prefix/\<auto-scaling-group-name\>* no more actions will be taken. If you have configured a parameter for your Auto Scaling group, the Lambda function will call Run Command with the commands you have set up. Both String and StringList parameters are valid. You can find an example Parameter for an Auto Scaling group named **SampleWebApp-AutoScalingGroup-1CRZJOLJHNXBI** on the image below.

![Parameter Store Example](/ec2-spot-interruption-handler/images/ParameterStore.png)

You can test this with an existing Auto Scaling group on your account or deploying the sample web application CloudFormation template on the sample-asg folder.

## Costs of the solution

- Amazon EventBridge events for AWS service events are free of charge. Pricing details can be found [here](https://aws.amazon.com/eventbridge/pricing/)
- If you already use all the monthly free tier that AWS Lambda provides, Lambda pricing applies. Otherwise, the usage of this will be covered by the free tier. More info [here](https://aws.amazon.com/lambda/pricing/)
- AWS Systems Manager Run Command doesn't incurr additional charges (limits apply). Parameter Store has also a Standard tier that doesn't incurr charges. Pricing details can be found [here](https://aws.amazon.com/cloudwatch/pricing/)