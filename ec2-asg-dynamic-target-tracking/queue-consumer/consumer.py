
# Import modules
import boto3
import json
import time
from pprint import pprint
import logging
from botocore.exceptions import ClientError
from botocore.config import Config

# Create logger
logging.basicConfig(filename='consumer.log', level=logging.INFO)
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
ssm = session.client('ssm', config=config)

# Initialize variables (from param store)
response = ssm.get_parameter(Name='ProcessingQueueName')
queueName = response['Parameter']['Value']


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

if __name__=="__main__":

    # Initialize variables
    queue = sqs.get_queue_by_name(QueueName=queueName)
    batchSize = 1
    queueWaitTime= 5

    # start continuous loop
    logger.info('Starting queue consumer process...')
    while True: 

        try:
            
            # Read messages from queue
            logger.info('Polling messages from the processing queue')
            messages = queue.receive_messages(AttributeNames=['All'], MaxNumberOfMessages=batchSize, WaitTimeSeconds=queueWaitTime) 
            if not messages: continue
            logger.info('-- Received {} messages'.format(len(messages)))
            
            # Process messages
            for message in messages:
                
                # Process message
                logger.info('---- Processing message {}...'.format(message.message_id))
                messageBody = json.loads(message.body)
                processingDuration = messageBody.get('duration')
                time.sleep(processingDuration)
                
                # Delete the message
                message.delete()
                logger.info('---- Message processed and deleted')
                
                # Report message duration to cloudwatch
                publishMetricValue('ASG-Metrics', 'MsgProcessingDuration', processingDuration)


        except ClientError as error: 
            logger.error('SQS Service Exception - Code: {}, Message: {}'.format(error.response['Error']['Code'],error.response['Error']['Message']))
            continue   

        except Exception as e: 
            logger.error('Unexpected error - {}'.format(e))


