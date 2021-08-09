
# Copyright 2020 Amazon.com, Inc. or its affiliates. All Rights Reserved.
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

#####################
# Example script that demonstrates paginated describe calls for EC2 Spot Instance Requests.
# First, the script makes a paginated call to get all Spot Fleet Request Ids from a Spot Fleet,
# Then, it makes a paginated call to describe each Spot Fleet Request Id to obtain additional details.
# This pattern can be repeated for any Describe call that supports pagination.
#####################

import boto3

ec2 = boto3.client('ec2')

def describe_spot_instance_requests(request_ids):
    described_spot_instance_requests = []

    # Create Paginator and Page Iterator for DescribeInstances
    paginator = ec2.get_paginator('describe_spot_instance_requests')
    page_iterator = paginator.paginate(SpotInstanceRequestIds=request_ids)

    # Iterate Pages and Add Instances To List
    for page in page_iterator:
        for request in page['SpotInstanceRequests']:
            described_spot_instance_requests.append(request)

    return described_spot_instance_requests

def get_spot_instance_requsts_from_fleet(fleet_id):
    
    described_spot_instance_requests = []

    # Create Paginator and Page Iterator for DescribeInstances
    paginator = ec2.get_paginator('describe_spot_fleet_instances')
    page_iterator = paginator.paginate(SpotFleetRequestId=fleet_id)

    # Iterate Pages and Add Instances To List
    for page in page_iterator:
        for instance in page['ActiveInstances']:
            described_spot_instance_requests.append(instance['SpotInstanceRequestId'])

    return described_spot_instance_requests

if __name__ == "__main__":

    spot_fleet_id = "[REQUEST_ID_GOES_HERE]" # Replace With Your Spot Fleet Request ID

    # First, Get all Spot Fleet Request IDs in a Fleet Request
    spot_fleet_request_ids = get_spot_instance_requsts_from_fleet(spot_fleet_id)

    # Next, Describe Each Spot Fleet Request
    described_spot_fleet_requests = describe_spot_instance_requests(spot_fleet_request_ids)

    # Use Results as Needed
    print(described_spot_fleet_requests)