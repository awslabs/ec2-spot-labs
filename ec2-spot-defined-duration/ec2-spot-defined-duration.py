#!/usr/bin/env python3

# Authors:
#    Description: Chad Schmutzer (schmutze@amazon.com)
#  License:
#    Description: 'Copyright 2019 Amazon.com, Inc. and its affiliates. All Rights Reserved.
#
#      Licensed under the Amazon Software License (the "License"). You may not use this file
#      except in compliance with the License. A copy of the License is located at
#
#      http://aws.amazon.com/asl/
#
#      or in the "license" file accompanying this file. This file is distributed on an "AS IS"
#      BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#      License for the specific language governing permissions and limitations under the License.'

import boto3

instanceType = 'c4.large'
imageId = 'ami-0de53d8956e8dcf80'
maxCount = 3
minCount = 3
definedDuration = 60
subnet1a = 'subnet-0fc4d2543f3dcc255'
subnet1b = 'subnet-09b9d0dbca4bae8a5'
subnet1c = 'subnet-0437dfe009676c434'

client = boto3.client('ec2')

# create the placement group
try:
  response = client.create_placement_group(
    GroupName = 'myPlacementGroup',
    Strategy = 'cluster'
  )
  print(response)
except:
  # skip if already exists
  print("Error creating placement group (perhaps it already exists). Skipping creation.")

# create the launch template
try:
  response = client.create_launch_template(
    LaunchTemplateName = 'myLaunchTemplate',
    VersionDescription = 'My launch template for Spot Blocks with subnet 1a',
    LaunchTemplateData = {
      'NetworkInterfaces': [
        {
          'DeviceIndex': 0,
          'SubnetId': subnet1a
        }
      ],
      'ImageId': imageId,
      'InstanceType': instanceType,
      'Placement': {
        'GroupName': 'myPlacementGroup'
      },
      'TagSpecifications': [
        {
          'ResourceType': 'instance',
          'Tags': [
            {
              'Key': 'Name',
              'Value': 'myClusterInstance'
            }
          ]
        }
      ],
      'InstanceMarketOptions': {
        'MarketType': 'spot',
        'SpotOptions': {
          'SpotInstanceType': 'one-time',
          'BlockDurationMinutes': definedDuration
        }
      }        
    }
  )
  print(response)
except:
  print("Error creating launch template (perhaps it already exists). Skipping create.")

# create new launch template version with secondary subnet
try:
  response = client.create_launch_template_version(
    LaunchTemplateName = 'myLaunchTemplate',
    SourceVersion = '1',
    VersionDescription = 'My launch template for Spot Blocks with subnet 1b',
    LaunchTemplateData = {
      'NetworkInterfaces': [
        {
          'DeviceIndex': 0,
          'SubnetId': subnet1b
        }
      ]
    }
  )
  print(response)
except:
  print("Error creating launch template version (perhaps it already exists). Skipping create.")

# create new launch template version with tertiary subnet
try:
  response = client.create_launch_template_version(
    LaunchTemplateName = 'myLaunchTemplate',
    SourceVersion = '1',
    VersionDescription = 'My launch template for Spot Blocks with subnet 1c',
    LaunchTemplateData = {
      'NetworkInterfaces': [
        {
          'DeviceIndex': 0,
          'SubnetId': subnet1c
        }
      ]
    }
  )
  print(response)
except:
  print("Error creating launch template version (perhaps it already exists). Skipping create.")

# loop through all versions (subnets) of the launch template, requesting the defined duration Spot Instances
versions = ['1', '2', '3']
for i in versions:
  try:
    response = client.run_instances(
      LaunchTemplate = {
        'LaunchTemplateName': 'myLaunchTemplate',
        'Version': i
      },
      MaxCount = 3,
      MinCount = 3
    )
    print(response)
    break
  except:
    print("Error calling runInstances with launch template version", i)

# delete the launch template and all versions
try:
  response = client.delete_launch_template(
    LaunchTemplateName = 'myLaunchTemplate'
  )
  print(response)
except:
  print("Error deleting launch template. Skipping delete.")

# delete the placement group
try:
  response = client.delete_placement_group(
    GroupName='myPlacementGroup'
  )
except:
  print("Error deleting placement group. Skipping delete.")
