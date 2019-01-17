#!/usr/bin/env python

# Authors:
#    Description: Chad Schmutzer (schmutze@amazon.com)
#  License:
#    Description: 'Copyright 2017 Amazon.com, Inc. and its affiliates. All Rights Reserved.
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

client = boto3.client('emr')

response = client.run_job_flow(
    Name='myEmrSpotCluster',
    ReleaseLabel='emr-5.20.0',
    JobFlowRole='EMR_EC2_DefaultRole',
    ServiceRole='EMR_DefaultRole',
    Instances={
        'InstanceFleets': [
            {
                'Name': 'master',
                'InstanceFleetType': 'MASTER',
                'TargetOnDemandCapacity': 0,
                'TargetSpotCapacity': 1,
                'InstanceTypeConfigs': [
                    {
                        'InstanceType': 'c4.xlarge'
                    },
                    {
                        'InstanceType': 'm4.xlarge'
                    },
                    {
                        'InstanceType': 'r4.xlarge'
                    }
                ],
                'LaunchSpecifications': {
                    'SpotSpecification': {
                        'TimeoutDurationMinutes': 60,
                        'TimeoutAction': 'SWITCH_TO_ON_DEMAND',
                    }
                }
            },
            {
                'Name': 'core',
                'InstanceFleetType': 'CORE',
                'TargetOnDemandCapacity': 0,
                'TargetSpotCapacity': 2,
                'InstanceTypeConfigs': [
                    {
                        'InstanceType': 'c4.xlarge'
                    },
                    {
                        'InstanceType': 'm4.xlarge'
                    },
                    {
                        'InstanceType': 'r4.xlarge'
                    }
                ],
                'LaunchSpecifications': {
                    'SpotSpecification': {
                        'TimeoutDurationMinutes': 60,
                        'TimeoutAction': 'SWITCH_TO_ON_DEMAND',
                    }
                }
            },
            {
                'Name': 'master',
                'InstanceFleetType': 'TASK',
                'TargetOnDemandCapacity': 0,
                'TargetSpotCapacity': 4,
                'InstanceTypeConfigs': [
                    {
                        'InstanceType': 'c4.xlarge'
                    },
                    {
                        'InstanceType': 'm4.xlarge'
                    },
                    {
                        'InstanceType': 'r4.xlarge'
                    }
                ],
                'LaunchSpecifications': {
                    'SpotSpecification': {
                        'TimeoutDurationMinutes': 60,
                        'TimeoutAction': 'SWITCH_TO_ON_DEMAND',
                    }
                }
            }
        ],
        'Ec2SubnetIds': [ 'subnet-05ef7d72', 'subnet-fa2653a3', 'subnet-dc1c12b9' ]
    },
    Applications=[
        {
            'Name': 'Spark'
        }
    ]
)