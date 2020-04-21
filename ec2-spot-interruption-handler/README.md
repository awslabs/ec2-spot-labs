# Spot Instance Interruption Handler

Spot instances are spare EC2 capacity offered with an up to 90% discount compared to On-Demand pricing with the only consideration that they can be reclaimed with a two-minute warning if EC2 needs the capacity back. This two minutes warning is provided via the local EC2 metadata endpoint of each instance type (http://169.254.169.254/latest/meta-data/spot/instance-action) and via a CloudWatch event, which can trigger a set of actions.

This project provides a CloudFormation template that deploys a CloudWatch Events rule that catches Spot Instance Interruptions and triggers an AWS Lambda function to react to it. On its current form, this Lambda function allows you to react to Spot instance interruptions of instances that are part of an Auto Scaling group within the region you deploy it. When receiving an interruption notice, the function calls the Auto Scaling API to detach the instance from the Auto Scaling group, if the group has a Load Balancer configured, it will put the instance in draining state to stop sending new requests to it and allow time for in-flight requests to complete (default settings for ALB is 300 seconds, but it's recommended to adjust deregistration delay to 90 seconds or lower for Spot instances; see docs [here](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/load-balancer-target-groups.html#deregistration-delay)); as well as request Auto Scaling to attempt to launch a replacement instance based on your instance type selection and allocation strategy. You can find more information [here](https://docs.aws.amazon.com/autoscaling/ec2/APIReference/API_DetachInstances.html).

Optionally, you can also configure a set of commands to be invoked on your to-be-interrupted instance using AWS Systems Manager [Run Command](https://docs.aws.amazon.com/systems-manager/latest/userguide/execute-remote-commands.html); like gracefully terminating your application, copying logs to S3, deregistering agents... In order to use this feature, your instances need to run the Systems Manager agent (that comes pre-installed on Amazon Linux 2) and have an IAM Instance Profile with permissions to access the Systems manager API. You can find more configuration details [here](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-setting-up.html).

You can set up commands you want to execute when your Spot Instances on a specific Auto Scaling group are interrupted by creating a parameter within AWS Systems Manager [Parameter Store](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-parameter-store.html) with the commands you want to run. The Lambda function checks if a Parameter exists for the Auto Scaling group that the instance belongs to, if it exists, it will then call RunCommand referencing the parameter, otherwise the function finishes here. With default settings, the parameter name needs to be "/spot-instance-interruption-handler/run_commands/<auto-scaling-group-name>".

![Architecture](/ec2-spot-interruption-handler/images/architecture.png)

You can delay the execution of termination commands to x seconds before the Spot instance interruption if, for example, you're allowing time for in-flight http requests to complete; before you graceuflly stop your application using the wait_x_seconds_before_interruption.sh bash script (it defaults to 30 seconds before interruption, but you can pass your desired time as parameter. It also requires [jq](https://stedolan.github.io/jq/) installed on the instance). Below you can find an example.

```bash
curl -s -o /tmp/wait_x_seconds_before_interruption.sh "https://raw.githubusercontent.com/awslabs/ec2-spot-labs/master/ec2-spot-interruption-handler/wait_x_seconds_before_interruption.sh"; chmod u+x /tmp/wait_x_seconds_before_interruption.sh; /tmp/wait_x_seconds_before_interruption.sh 60; echo "executing termination commands"
```

Both the Lambda function execution and the output of your commands is logged on CloudWatch logs on the /aws/lambda/SpotInterruptionHandler and /aws/ssm/AWS-RunShellScript log groups respectively.

## Set Up instructions

To set up the Spot interruption handler, follow these steps:

1. Clone this repository to your local machine
1. ZIP the Lambda function (index.py)
1. Upload the zipped Lambda function to an Amazon S3 Bucket in the region
1. Deploy the cloudformation.yml template and fill in the parameters
  - LambdaFunctionS3Bucket: The name of the S3 bucket where you have uploaded the zipped function.
  - LambdaFunctionS3Key: The S3 key where you have uploaded the zipped function
  - ASGSSMParameterPrefix: The prefix of your Systems Manager Parameters where you will configure the commands you will run on the different ASGs. This defaults to /spot-instance-interruption-handler/run_commands/. If you leave the default settings, your parameters will need to be named "/spot-instance-interruption-handler/run_commands/<auto-scaling-group-name>"
  - EnableRunCommandOutputLogging: Enable logging to CloudWatch logs of the output of RunCommand (by default is set to True, you can disable it setting this to False)

Once the CloudFormation template is deployed, the Spot Interruption Handler will trigger upon Spot interruption and put the to-be-interrupted instance in draining state and launch replacement capacity for your instances that are part of an Auto Scaling group. If there are no Parameters in Systems Manager matching your prefix/<auto-scaling-group-name> no more actions will be taken. If you have configured parameters for your Auto Scaling group, the Lambda function will call Run Command with the commands you have set up. Both String and StringList parameters are valid. You can find an example on the image below.

![Parameter Store Example](/ec2-spot-interruption-handler/images/ParameterStore.png)

You can test this with an existing Auto Scaling group on your account or deploying the sample web application on the sample-asg folder.

## Costs of the solution

- CloudWatch Events (except custom events) are free of charge. Pricing details can be found [here](https://aws.amazon.com/cloudwatch/pricing/)
- If you already use all the monthly free tier that AWS Lambda provides, Lambda pricing applies. Otherwise, the usage of this will be covered by the free tier. More info [here](https://aws.amazon.com/lambda/pricing/)
- AWS Systems Manager Run Command doesn't incurr additional charges (limits apply). Parameter Store has also a Standard tier that doesn't incurr charges. Pricing details can be found [here](https://aws.amazon.com/cloudwatch/pricing/)