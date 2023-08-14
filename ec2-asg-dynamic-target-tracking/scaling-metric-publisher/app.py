
# Import modules
import boto3
import os
from pprint import pprint
import logging
from botocore.exceptions import ClientError
from botocore.config import Config

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
sqs = session.resource('sqs', config=config)
cloudwatch = session.client('cloudwatch', config=config)
autoscaling = session.client('autoscaling', config=config)

# Read  environment variables
queueName = os.environ['queueName']
asgName = os.environ['asgName']


def publishMetricValue(namespace, metricName, value, metricType):

    response = cloudwatch.put_metric_data(
        Namespace = namespace,
        MetricData = [
            {
                'MetricName': metricName,
                'Value': value,
                'Dimensions': [
                    {
                        'Name': 'Type',
                        'Value': metricType
                    }
                ],
                'StorageResolution': 1
            }
        ]
    )

def getInServiceInstances(asgName): 
    
    # Describe ASG
    response = autoscaling.describe_auto_scaling_groups(AutoScalingGroupNames=[asgName], MaxRecords=100)
    instances = response['AutoScalingGroups'][0]['Instances']
    
    # Extract number of instances
    inServiceInstances = [instance for instance in instances if instance['LifecycleState'] == 'InService']
    return len(inServiceInstances)



def lambda_handler(event, context):


    # Get number of messages in queue
    processingQueue = sqs.get_queue_by_name(QueueName=queueName)
    nMessagesVisible = int(processingQueue.attributes.get('ApproximateNumberOfMessages'))
    print('There is a total of {} messages in the processing queue(s)'.format(nMessagesVisible))

    # Get number of instances in ASG
    nInstances = getInServiceInstances(asgName)
    print('Total InService Instances in ASG: {}'.format(nInstances))

    # Publish metric data to cloudwatch
    BPI = nMessagesVisible / nInstances
    publishMetricValue('ASG-Metrics', 'BPI', BPI, 'Single Queue')
    print('A Backlog per instance (BPI) of {} was published to CloudWatch'.format(BPI))


