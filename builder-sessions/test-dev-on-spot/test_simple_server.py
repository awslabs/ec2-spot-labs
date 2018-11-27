#!/usr/bin/python

"""
Licensed under the Amazon Software License (the "License"). You may not use this file
except in compliance with the License. A copy of the License is located at
http://aws.amazon.com/asl/
or in the "license" file accompanying this file. This file is distributed on an "AS IS"
BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
License for the specific language governing permissions and limitations under the License.'

Sends GET requests to the specified target host and posts metrics
to CloudWatch based on the result. This will start one testing
thread per CPU.

Usage:
  ./test_simple_server.py <aws_region> <target_hostname>
"""

import boto3
import multiprocessing
import requests
import sys
from threading import Thread
import time

METRIC_BATCH_SIZE = 10

def make_call(hostname):
    try:
        r = requests.get("http://"+hostname, timeout=5.0)
        r.raise_for_status()
        return True
    except:
        return False

def emit_metrics(cloudwatch_client, successes, errors):
    metric_data = []
    for i in range(successes):
        metric_data.append({"MetricName": "Success", "Value": 1})
        metric_data.append({"MetricName": "Error", "Value": 0})
    for i in range(errors):
        metric_data.append({"MetricName": "Success", "Value": 0})
        metric_data.append({"MetricName": "Error", "Value": 1})
    cloudwatch_client.put_metric_data(Namespace="ReInvent-EC2SpotTestDev-Metrics", MetricData=metric_data)

def rate_limit(start):
    elapsed = time.time() - start
    if (elapsed < 1.0):
        time.sleep(1.0 - elapsed)

def start_test_loop(cloudwatch_client, hostname):
    while True:
        successes = 0
        errors = 0
        for i in range(METRIC_BATCH_SIZE):
            start = time.time()
            is_success = make_call(hostname)
            if is_success:
                successes += 1
            else:
                errors += 1
            rate_limit(start)
        emit_metrics(cloudwatch_client, successes, errors)

aws_region = sys.argv[1]
cloudwatch_client = boto3.client('cloudwatch', region_name=aws_region)
hostname = sys.argv[2]
cpu_count = multiprocessing.cpu_count()
for i in range(cpu_count):
    t = Thread(target=start_test_loop, args=(cloudwatch_client, hostname))
    t.start()
