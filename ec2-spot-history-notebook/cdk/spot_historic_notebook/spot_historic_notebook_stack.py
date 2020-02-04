
from aws_cdk import (
    aws_iam as iam_,
    aws_sagemaker as sagemaker_,
    core)

import os
import boto3
import uuid


DEFAULT_GITHUB_REPO="https://github.com/ruecarlo/ec2-spot-labs.git"

profile = os.getenv("AWS_PROFILE", "default")
session = boto3.Session(profile_name=profile)
my_region = session.region_name
my_acc_id = session.client('sts').get_caller_identity().get('Account')
ec2client = session.client('ec2')
smclient = session.client('sagemaker')

#USER VARIABLES
default_vpc = [x['VpcId'] for x in ec2client.describe_vpcs()['Vpcs'] if x['IsDefault']][0]
default_sg = [x['GroupId'] for x in ec2client.describe_security_groups(Filters=[{'Name':'vpc-id','Values':[default_vpc,]},])['SecurityGroups'] if x['GroupName']=='default']
default_subnet = [x['SubnetId'] for x in ec2client.describe_subnets(Filters=[{'Name':'vpc-id','Values':[default_vpc,]},])['Subnets'] if x['DefaultForAz']][0]



class CdkSpotHistoricNotebookStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create role for Notebook instance
        nrole = iam_.Role(
            self,
            "notebookAccessRole"
        )

        nrole.add_managed_policy(iam_.ManagedPolicy.from_aws_managed_policy_name('AmazonEC2ReadOnlyAccess'))


        notebook_uuid=str(uuid.uuid4())
        notebook_uuid=str(notebook_uuid[0:notebook_uuid.find('-')])
        notebook_instance_id = 'spot-history-notebook-'+notebook_uuid
        print("id {}".format(notebook_instance_id))

        notebook_instance = sagemaker_.CfnNotebookInstance(
            self,
            notebook_instance_id,
            instance_type='ml.m5.large',
            volume_size_in_gb=10,
            security_group_ids=default_sg,
            subnet_id=default_subnet,
            notebook_instance_name=notebook_instance_id,
            role_arn=nrole.role_arn,
            default_code_repository=DEFAULT_GITHUB_REPO
        )

        core.CfnOutput(
            self,
            "Notebook Name",
            value=notebook_instance.notebook_instance_name,
            description="Notebook Instance Name",  # Optional
        )
