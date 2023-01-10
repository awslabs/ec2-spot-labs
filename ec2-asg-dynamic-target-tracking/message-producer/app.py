
# Import modules
import boto3
import os
import random
import os 
import struct
import json
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
# cloudwatch = session.client('cloudwatch', config=config)
# autoscaling = session.client('autoscaling', config=config)

# Read  environment variables
queueName = os.environ['queueName']
defaultMsgProcDuration = int(os.environ['defaultMsgProcDuration'])

# Initialize other parameters
nMessages = 50

def lambda_handler(event, context):

    # Get the queue
    queue = sqs.get_queue_by_name(QueueName=queueName)

    # Send N messages
    for i in range(nMessages): 
        
        # Build Msg body
        randomNumber = struct.unpack('H', os.urandom(2))[0]
        messageBody = {"id": randomNumber, "duration": defaultMsgProcDuration}
        print('Sending message id: {}'.format(randomNumber))

        # Call API
        response = queue.send_message(
            MessageBody=json.dumps(messageBody), 
            MessageGroupId=str(messageBody['id']),
            MessageDeduplicationId=str(messageBody['id']) + ':' + str(randomNumber),
        )


