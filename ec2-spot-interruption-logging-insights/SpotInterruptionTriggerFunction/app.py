 # Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
 #
 # Permission is hereby granted, free of charge, to any person obtaining a copy of this
 # software and associated documentation files (the "Software"), to deal in the Software
 # without restriction, including without limitation the rights to use, copy, modify,
 # merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
 # permit persons to whom the Software is furnished to do so.
 #
 # THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
 # INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
 # PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
 # HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
 # OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
 # SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import boto3
import os
import uuid
import time
import datetime
import json

from botocore.exceptions import ClientError

ec2client = boto3.client('ec2')
logclient = boto3.client('logs')

cloudwatch_log_group_name = os.environ['CLOUDWATCH_LOG_GROUP_NAME']

def lambda_handler(event, context):

    print(event)

    # Get Instance ID
    instance_id = event['detail']['instance-id']
    instance_details = {}

    # Describe Instance Details
    try:
        response = ec2client.describe_instances(
            InstanceIds=[instance_id]
            )

        print(response)
        instance_details = response['Reservations'][0]['Instances'][0]

    except ClientError as e: 
        print("Unexpected error: %s" % e)

    # Create CloudWatch Log Stream
    try: 
        now = datetime.datetime.now()
        cloudwatch_stream_name = '{}/{}/{}/{}/{}'.format(now.year, now.month, now.day, now.hour, uuid.uuid4().hex)

        response = logclient.create_log_stream(
            logGroupName=cloudwatch_log_group_name,
            logStreamName=cloudwatch_stream_name
        )
        print(response)
    except ClientError as e: 
        if e.response['Error']['Code'] == 'ResourceAlreadyExistsException':
            print("CloudWatch Stream Exists: %s" % cloudwatch_stream_name)
        else:
            print("Unexpected error: %s" % e)

    # Write Event to CloudWatch Log Stream
    try:
        log_event= {
            'Event': event,
            'InstanceDetails' : {
                'InstanceId':   instance_details['InstanceId'],
                'InstanceType': instance_details['InstanceType'],
                'Placement':    instance_details['Placement'],
                'Tags':         instance_details['Tags']
            },
        }

        print(log_event)

        response = logclient.put_log_events(
            logGroupName=cloudwatch_log_group_name,
            logStreamName=cloudwatch_stream_name,
            logEvents=[ 
                {
                    'timestamp': int(round(time.time() * 1000)),
                    'message': json.dumps(log_event)
                }
            ]
        )

        # TODO: If reusing the CloudWatch Log Stream then you'll need to handle the nextSequenceToken:
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.put_log_events
        
        print(response)        

    except ClientError as e: 
        print("Unexpected error: %s" % e)

    # End
    print('Execution Complete')
    return
