## Simulate an Interruption

This CloudFormation template deploys a simple web application on an Auto Scaling group composed of Spot instances fronted by an Application Load Balancer. The instances run Amazon Linux 2 which comes with the SSM agent installed and they're configured with an IAM Instance Profile in order to receive commands from Systems Manager and log the output in CloudWatch logs. They run a simple httpd server showing plain text displaying the instance id, instance type and AZ.

The template creates also a Systems Manager Parameter where you can specify commands when receiving a Spot Interruption notice for instances of the Auto Scaling group it creates; by default it just executes 'echo hello world' for demo purposes. All these configurations can be modified on the CloudFormation template parameters.

### To simulate an interruption:
1. Go to the AWS Lambda [console](https://console.aws.amazon.com/lambda/home?2#/functions) and open the Interruption handling function. 

1. On the top-right side of the screen, click on "Select a test event" and then "Configure test events"

1. On "Event name" type "Spot Instance Interruption", and on the actual event, copy the following sample interruption event:
   ```javascript
    {
      "version": "0",
      "id": "92453ca5-5b23-219e-8003-ab7283ca016b",
      "detail-type": "EC2 Spot Instance Interruption Warning",
      "source": "aws.ec2",
      "account": "123456789012",
      "time": "2020-04-05T11:03:11Z",
      "region": "eu-west-1",
      "resources": [
        "arn:aws:ec2:eu-west-1b:instance/<instance-id>"
      ],
    "detail": {
      "instance-id": "<instance-id>",
      "instance-action": "terminate"
      }
    }
   ```
1. On a separate browser window, open the EC2 Console and copy the instance id of one of the instances you want to simulate the interruption for, and paste it on the placeholders <instance-id> of the interruption event above to mock a Spot interruption. Then click on "Create" to save the interruption event.

1. On the Lambda console, click on "Test" to execute the Lambda function with the mock event. On the logs, you should see something similar to this:
    ```
    START RequestId: f7f511dd-310e-42b2-bda0-d7a9c7ece68c Version: $LATEST
    [INFO]	2020-04-22T19:18:49.900Z	f7f511dd-310e-42b2-bda0-d7a9c7ece68c	Handling spot instance interruption notification for instance i-04bcbb54d672a6986
    [INFO]	2020-04-22T19:18:50.402Z	f7f511dd-310e-42b2-bda0-d7a9c7ece68c	At 2020-04-22T19:18:50Z instance i-xxxxx was detached in response to a user request.
    [INFO]	2020-04-22T19:18:50.402Z	f7f511dd-310e-42b2-bda0-d7a9c7ece68c	INFO: Instance i-xxxxx has been successfully detached from    SampleApp-SampleWebAppAutoScalingGroup-KZZNN7T2110M
    [INFO]	2020-04-22T19:18:50.684Z	f7f511dd-310e-42b2-bda0-d7a9c7ece68c	Running commands on instance i-xxxxx. Command id: 11ae52df-771c-49f7-bc66-ee20ea4d25f4 
    [INFO]	2020-04-22T19:18:50.684Z	f7f511dd-310e-42b2-bda0-d7a9c7ece68c	Interruption response actions completed for instance i-xxxxx belonging to     SampleApp-SampleWebAppAutoScalingGroup-KZZNN7T2110M
    END RequestId: f7f511dd-310e-42b2-bda0-d7a9c7ece68c	
    ```

1. Go to the EC2 Auto Scaling [console](https://console.aws.amazon.com/ec2/autoscaling/home?#AutoScalingGroups:) and select the Auto Scaling group of your instance. You will see the instance is in "draining" mode and also a replacement instance has been launched. 

1. Go to the Target Groups section of the EC2 [Console](https://console.aws.amazon.com/ec2/v2/home?#TargetGroups:sort=targetGroupName) and select the Target Group where your instance belongs. Click on the "Targets" tab and under registered targets, you will see the instance on "draining" mode

1. Go to the CloudWatch Logs [console](https://console.aws.amazon.com/cloudwatch/home?#logs:) to view the command execution logs. 

1. Now go to the EC2 console and manually terminate the instance you used to simulate the interruption as it's no longer part of the Auto Scaling group and otherwise will be kept running.

1. Go to the Systems Manager console and click on the [Parameters](https://console.aws.amazon.com/systems-manager/parameters?) section. You will find the parameter created by the Cloudformation template. Feel free to edit it to customize the commands to execute on interruption.
