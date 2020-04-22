import boto3
from botocore.exceptions import ClientError
import logging, os

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# API Clients
ec2client = boto3.client('ec2')
asgclient = boto3.client('autoscaling')
ssmclient = boto3.client('ssm')


def get_asg_from_instance_id(instance_id):
    # Describe tags for the instance that will be interrupted
    try:
        instanceDescr = ec2client.describe_instances(InstanceIds=[instance_id])
        describeTags = instanceDescr['Reservations'][0]['Instances'][0]
    except ClientError as e:
        error_message = "Unable to describe tags for instance id: {id}. ".format(id=instance_id) 
        logger.error( error_message + e.response['Error']['Message'])
        # Instance does not exist or cannot be described
        raise e

    # Check if the instance belongs to ASG
    for tag in describeTags['Tags']:
        if tag['Key'] =='aws:autoscaling:groupName':
            # ASG group found, returns the autoscaling group name
            return tag['Value']
    
    # The instance exists, but doesn't seem to be part of an ASG
    return None

def detach_instance_from_asg(instance_id,as_group_name):
    try:
        # detach instance from ASG and launch replacement instance
        response = asgclient.detach_instances(
            InstanceIds=[instance_id],
            AutoScalingGroupName=as_group_name,
            ShouldDecrementDesiredCapacity=False)
        logger.info(response['Activities'][0]['Cause'])
    except ClientError as e:
        error_message = "Unable to detach instance {id} from AutoScaling Group {asg_name}. ".format(
            id=instance_id,asg_name=as_group_name)
        logger.error( error_message + e.response['Error']['Message'])
        raise e

def asg_has_defined_interruption_commands(asg_name):
    # Check if an SSM parameter store with interruption commandshas been set up 
    # for the Auto Scaling group 
    
    ssm_parameter_name = os.environ['ASGSSMParameterPrefix'] + asg_name
    
    try:
        ssmclient.get_parameter(Name=ssm_parameter_name)
        return True
    except ssmclient.exceptions.ParameterNotFound:
        return None

def run_commands_on_instance(instance_id, asg_name):
    # SSM RunCommand RunShellScript with commands configured in ParameterStore

    parameter_store_commands = ["{{ssm:" + os.environ['ASGSSMParameterPrefix'] + asg_name + "}}"]
    
    # Reference commands directly from SSM Parameter Store, limit execution timeout to 2 minutes
    document_parameters= {
        'commands': parameter_store_commands,
        'executionTimeout': ["120"]
    }
    
    # Configure SSM RunCommand Logging to CloudWatchLogs
    cloudwatch_output_config = {
        'CloudWatchOutputEnabled' : bool(os.environ['EnableRunCommandOutputLogging']) 
    }

    # Send Command to the instance
    try:
        response = ssmclient.send_command(
            InstanceIds=[instance_id],
            DocumentName='AWS-RunShellScript',
            Parameters=document_parameters,
            CloudWatchOutputConfig=cloudwatch_output_config,
            TimeoutSeconds=30)
        logger.info("Running commands on instance {instanceid}. Command id: {id} ".format(
                instanceid=instance_id,id=response['Command']['CommandId']))
    except ClientError as e:
        error_message = "Could not execute commands on instance {id}. ".format(id=instance_id)
        logger.error( error_message + e.response['Error']['Message'])
        raise e
        
        
def handler(event, context):
    
    # Get instance Id from event
    instance_id = event['detail']['instance-id']
    logger.info("Handling spot instance interruption notification for instance {id}".format(
        id=instance_id))
    
    # Check the Auto Scaling group where the instance belongs
    auto_scaling_group_name = get_asg_from_instance_id(instance_id)

    if auto_scaling_group_name is None:
        info_message = "No action taken. Instance {id} does not belong to an AutoScaling group.".format(
            id=instance_id) 
        
        logger.info(info_message)
        return(info_message)
    
    # Detach instance from ASG
    detach_instance_from_asg(instance_id, auto_scaling_group_name)

    # If interruption commands have been set up for the Auto Scaling group, execute them
    if asg_has_defined_interruption_commands(auto_scaling_group_name):
        run_commands_on_instance(instance_id,auto_scaling_group_name)
    else:
        logging.info("No SSM Parameter with commands associated with Auto Scaling group {asg}".format(
            asg=auto_scaling_group_name))

    return("INFO: Instance {id} has been successfully detached from {asg_name}".format(
        id=instance_id,asg_name=auto_scaling_group_name))