
# Import modules
import boto3
import os
from pprint import pprint
import logging
from botocore.exceptions import ClientError
from botocore.config import Config
from datetime import datetime
from datetime import timedelta

# Create logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# Define config
config = Config(
   retries = {
      'max_attempts': 10,
      'mode': 'standard'
   }
)

# Define session and resources
session = boto3.Session()
# sqs = session.resource('sqs', config=config)
cloudwatch = session.client('cloudwatch', config=config)
autoscaling = session.client('autoscaling', config=config)

# Read environment variables
asgName = os.environ['asgName']
desiredLatency = int(os.environ['desiredLatency'])
defaultMsgProcDuration = int(os.environ['defaultMsgProcDuration'])

# Initialize variables
metricNamespace = "ASG-Metrics"
metricName = "MsgProcessingDuration"


def publishMetricValue(namespace, metricName, value):

    response = cloudwatch.put_metric_data(
        Namespace = namespace,
        MetricData = [
            {
                'MetricName': metricName,
                'Value': value,
                'StorageResolution': 1
            }
        ]
    )


def getMetricValue(metricNamespace, metricName):

    # Define query
    query = {
        'Id': 'query_123',
        'MetricStat': {
            'Metric': {
                'Namespace': metricNamespace,
                'MetricName': metricName,
            },
            'Period': 1,
            'Stat': 'Average',
        }
    }

    response = cloudwatch.get_metric_data(
        MetricDataQueries=[query],
        StartTime=datetime.utcnow() - timedelta(seconds=86400),
        EndTime=datetime.utcnow(),
    )

    if not response.get('MetricDataResults')[0].get('Values'): 
        msgProcessingDuration = defaultMsgProcDuration
    else: 
        msgProcessingDuration = response.get('MetricDataResults')[0].get('Values')[0]
        
    # Return 
    return msgProcessingDuration
    


def lambda_handler(event, context):

    # Get cloudwatch metric for msg processing duration
    msgProcessingDuration = getMetricValue(metricNamespace, metricName)
    print('Most recent message processing duration is {}'.format(msgProcessingDuration))

    # Calculate new target BPI (assuming latency of 5mins)
    newTargetBPI = int(desiredLatency / msgProcessingDuration)
    print('New Target BPI is {}'.format(newTargetBPI))

    # Get scaling policy of ASG
    response = autoscaling.describe_policies(AutoScalingGroupName=asgName, PolicyTypes=['TargetTrackingScaling'])
    policies = response.get('ScalingPolicies')    
    policy = policies[0]
    print(policy)

    # Get target tracking config and update target value
    TargetTrackingConfig = policy.get('TargetTrackingConfiguration')
    TargetTrackingConfig['TargetValue'] = newTargetBPI

    # Update scaling policy of ASG
    autoscaling.put_scaling_policy(
        AutoScalingGroupName=policy.get('AutoScalingGroupName'), 
        PolicyName=policy.get('PolicyName'),
        PolicyType=policy.get('PolicyType'),
        TargetTrackingConfiguration=TargetTrackingConfig
    )    
    print('Scaling policy of ASG has been successfully updated!')

    # Publish new target BPI
    publishMetricValue('ASG-Metrics', 'ASG-Target-BPI', newTargetBPI)


