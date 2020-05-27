# ec2-spot-interruption-logging-insights

This is a sample solution for logging instance details in response to EC2 Spot Instance Interruption Warnings and analyzing them with CloudWatch Log Insights. 

Using CloudWatch Events, an event rule subscribes to EC2 Spot Instance Interruption Warnings, and triggers a Lambda function which collects details about the instance being interrupted and logs that information to a CloudWatch Logs Group. The solution can be configured to log any details you require about your instance, and by default logs InstanceId, InstanceType and all Tags. This information can then be used to develop visualizations with CloudWatch Logs Insights.

## Overview

![Alt text](docs/diagram.png?raw=true "Diagram")

1. A CloudWatch Event Rule subscribes to EC2 Spot Instance Interruption Warning Events.

```
{
  "detail-type": [
    "EC2 Spot Instance Interruption Warning"
  ],
  "source": [
    "aws.ec2"
  ]
}
```

2. The CloudWatch Event Rule triggers a Lambda function in response to these events.
3. The Lambda Function retrieves the instance ID from the Lambda Event Context (data sent to the Lambda function by CloudWatch Events).
4. The Lambda Function makes a DescribeInstances call EC2 to retrieve data about the EC2 Instance that is schedule for interruption.
5. The Lambda Function creates a CloudWatch Log Stream within a CloudWatch Log Group and Logs instance details to the CloudWatch Log Group (named via the CloudWatchLogGroupName parameter of the CloudFormation template).

```
{
    "Event": {
        "version": "0",
        "id": "ce5fd17f-ef3c-6f86-b99a-35e8d883b1d2",
        "detail-type": "EC2 Spot Instance Interruption Warning",
        "source": "aws.ec2",
        "account": "[REDACTED]",
        "time": "2019-07-10T13:57:04Z",
        "region": "us-west-2",
        "resources": [
            "arn:aws:ec2:us-west-2c:instance/i-0838c23d20458e79c"
        ],
        "detail": {
            "instance-id": "i-0838c23d20458e79c",
            "instance-action": "terminate"
        }
    },
    "InstanceDetails": {
        "InstanceId": "i-0838c23d20458e79c",
        "InstanceType": "c5.large",
        "Placement": {
            "AvailabilityZone": "us-west-2b",
            "GroupName": "",
            "Tenancy": "default"
        },        
        "Tags": [
            {
                "Key": "aws:ec2:fleet-id",
                "Value": "fleet-56e9a4cb-555f-ea91-a438-8b087e2181dd"
            },
            {
                "Key": "aws:ec2launchtemplate:version",
                "Value": "1"
            },
            {
                "Key": "aws:autoscaling:groupName",
                "Value": "SpotASG"
            },
            {
                "Key": "aws:ec2launchtemplate:id",
                "Value": "lt-0e85a5bd97a6d37ab"
            }
        ]
    }
}
```

6. Logs can then be reviewed and/or further processed for any required analysis. See the Analyzing Logs section below for some recommendations using CloudWatch Logs Insights.

## Packaging and Deployment

### Deployment (Severless Application Repository)

Search for ec2-spot-interruption-logging-insights in the [Serverless Application Repository]( https://serverlessrepo.aws.amazon.com/applications) and follow the instructions to deploy. (Make sure you've checked the box labeled: Show apps that create custom IAM roles or resource policies)

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
cd ec2-spot-labs/ec2-spot-interruption-logging-insights
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
    --stack-name ec2-spot-interruption-logging-insights \
    --capabilities CAPABILITY_IAM \
    --parameter-overrides \
    CloudWatchLogGroupName=REPLACE_THIS_WITH_THE_NAME_YOU_WANT \
    CloudWatchLogGroupRetentionPeriodDays=REPLACE_THIS_WITH_NUMBER_OF_DAYS_TO_RETAIN_LOGS  
```

## Analyzing Logs

### Example 1 - Interruptions Over Time

1. Logon to the AWS Console and Navigate to CloudWatch Console.
2. Click on the 'Logs/Insights' Link in the Left Menu Bar.
3. Enter your Log Group Name in the 'Select a log group' search bar.
4. Select a time period (to the right of the search bar).
5. Enter the following Query and then click 'Run query'.

```
fields @timestamp, @message
| sort @timestamp desc
```

6. You should now see a list of interruptions over the time span you've selected. You can expand each entry to see more details about the event (such as InstanceType, AvailabilityZone, and Instance Tags)

![Alt text](docs/analyze-1.png?raw=true "Log Analysis Example 1")

### Example 2 - Dashboard Visualizations

In addition to querying your log data, you can use CloudWatch Logs Insights to build dashboard visualizations.

1. Logon to the AWS Console and Navigate to CloudWatch Console.
2. Click on the 'Logs/Insights' Link in the Left Menu Bar.
3. Enter your Log Group Name in the 'Select a log group' search bar.
4. Select a time period (to the right of the search bar).
5. Enter the following Query and then click 'Run query'

```
stats count(*) by InstanceDetails.InstanceType
```

6. Click on the 'Visualization' tab.
7. Change the graph type to 'Bar'.
8. You should now see a visualization that shows count of interruptions by instance type for the time period you selected.

![Alt text](docs/analyze-2.png?raw=true "Log Analysis Example 2")

9. To add this to a CloudWatch Dashboard, click on the 'Actions' Button and select 'Add to Dashboard'.
10. If you have an existing dashboard you select it or create a new dashboard.
11. Give your new widget a name such as 'Interruptions By Instance Type' and click 'Add to dashboard'.

![Alt text](docs/analyze-3.png?raw=true "Log Analysis Example 3")

12. You'll be redirected to the Dashboard once it's created. From here you can adjust the time period using the selectors in the top right corner of the window. 

13. For example: Here's a dashboard that shows the count of interruptions by instance type for the past 3 hours.

![Alt text](docs/analyze-4.png?raw=true "Log Analysis Example 4")

14. Save your dashboard to commit any changes.

### Additional Examples

You can build additional dashboard widgets and further analyze your log data using CloudWatch Logs Insights' powerful query engine. You can learn more about CloudWatch Log Insights here: https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/AnalyzingLogData.html

