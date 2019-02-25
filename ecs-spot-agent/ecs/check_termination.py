#!/usr/local/bin/python -u

import os
import boto3
import requests
import traceback
from time import sleep
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(name)s %(levelname)s %(message)s')

check_interval = int(os.environ.get('CHECK_INTERVAL'))

class ECS():
    def __init__(self, region):
        self.client = boto3.client('ecs', region_name=region)
    def deregister(self, cluster, instance):
        res = client.deregister_container_instance(
            cluster=cluster,
            containerInstance=instance,
            force=True
        )


def get_region():
    logger.info('Check region from ec2 meta-data')
    availability_zone = requests.get('http://169.254.169.254/latest/meta-data/placement/availability-zone').text
    return availability_zone[0:-1]

def get_metadata():
    logger.info('Check ecs metadata from ecs-agent')
    res = requests.get('http://127.0.0.1:51678/v1/metadata')
    metadata = res.json()
    return metadata


if __name__ == '__main__':
    region = get_region()
    metadata = get_metadata()
    while True:
        try:
            res = requests.get('http://169.254.169.254/latest/meta-data/spot/termination-time')
            if res.status_code == 404:
                sleep(check_interval)
                continue
            elif res.status_code == 200:
                logger.warn('Deregister this instance from the cluster')
                ecs = ECS(region)
                ecs.deregister(metadata['Cluster'], metadata['ContainerInstanceArn'])
            else:
                raise Exception
        except Exception as e:
            break
            traceback.print_exc()
