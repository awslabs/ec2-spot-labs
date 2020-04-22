import boto3
from botocore.exceptions import ClientError
import logging, os

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# API Clients
ec2client = boto3.client('ec2')
asgclient = boto3.client('autoscaling')
ssmclient = boto3.client('ssm')


def get_interruption_handling_properties(instance_id):
    # Describe tags for the instance that will be interrupted
    try:
        describe_tags_response = ec2client.describe_instances(InstanceIds=[instance_id])
        instance_tags = describe_tags_response['Reservations'][0]['Instances'][0]['Tags']
    except ClientError as e:
        error_message = "Unable to describe tags for instance id: {id}. ".format(id=instance_id) 
        logger.error( error_message + e.response['Error']['Message'])
        # Instance does not exist or cannot be described
        raise e

    interruption_handling_properties = {
        'controller-type': '',
        'controller-id': '',
        'managed': False }
    
    # Check if instance belongs to an ASG or to a Spot Fleet
    for tag in instance_tags:
        if tag['Key'] == 'aws:autoscaling:groupName':
            # Instance belongs to an Auto Scaling group
            interruption_handling_properties['controller-type'] = 'auto-scaling-group'
            interruption_handling_properties['controller-id'] = tag['Value']
        elif tag['Key'] == 'aws:ec2spot:fleet-request-id':
            # Instance belongs to a Spot Fleet
            interruption_handling_properties['controller-type'] = 'spot-fleet'
            interruption_handling_properties['controller-id'] = tag['Value']
        elif tag['Key'] == 'SpotInterruptionHandler/enabled':
            interruption_handling_properties['managed'] = tag['Value'].lower() == 'true'

    return interruption_handling_properties

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

def controller_has_defined_interruption_commands(asg_name):
    # Check if an SSM parameter store with interruption commandshas been set up 
    # for the Auto Scaling group 
    
    ssm_parameter_name = os.environ['SSMParameterPrefix'] + asg_name
    
    try:
        ssmclient.get_parameter(Name=ssm_parameter_name)
        return True
    except ssmclient.exceptions.ParameterNotFound:
        return None

def run_commands_on_instance(instance_id, asg_name):
    # SSM RunCommand RunShellScript with commands configured in ParameterStore

    parameter_store_commands = ["{{ssm:" + os.environ['SSMParameterPrefix'] + asg_name + "}}"]
    
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
    except ssmclient.exceptions.InvalidInstanceId:
        logger.error ("SSM Agent is not running, or not registered to the endpoint or you don't have permissions to access the instance")
        raise e
    except ClientError as e:
        error_message = "Could not execute commands on instance {id}. ".format(id=instance_id)
        logger.error( error_message + e.response['Error']['Message'])
        raise e     
        
def handler(event, context):
    
    # Get instance Id from event
    instance_id = event['detail']['instance-id']
    logger.info("Handling spot instance interruption notification for instance {id}".format(
        id=instance_id))
    
    interruption_handling_properties = get_interruption_handling_properties(instance_id)
    
    #if the instance is tagged as managed and belongs to an Auto Scaling group or a Spot Fleet
    if interruption_handling_properties['managed']:
        if interruption_handling_properties['controller-id'] != '':
            # if it's an Auto Scaling group call detachInstances
            if interruption_handling_properties['controller-type'] == 'auto-scaling-group':
                detach_instance_from_asg(instance_id, interruption_handling_properties['controller-id'])
                logger.info("INFO: Instance {id} has been successfully detached from {asg_name}".format(
                id=instance_id,asg_name=interruption_handling_properties['controller-id']))

            # If interruption commands have been set up for the Auto Scaling group or Spot Fleet, execute them
            if controller_has_defined_interruption_commands(interruption_handling_properties['controller-id']):
                run_commands_on_instance(instance_id, interruption_handling_properties['controller-id'])
            else:
                logging.info("No SSM Parameter with commands associated with {controller} group {id}".format(
                    controller=interruption_handling_properties['controller-type'], id=interruption_handling_properties['controller-id']))
        else:
            info_message = "No action taken. Instance {id} is not part of an Auto Scaling group or Spot Fleet.".format(
                id=instance_id)
            logger.info(info_message)
            return(info_message)
    else:
        info_message = "No action taken. Instance {id} is not managed by SpotInterruptionHandler.".format(
            id=instance_id)
        logger.info(info_message)
        return(info_message)
 
    info_message = "Interruption response actions completed for instance {id} belonging to {controller}".format(
        id=instance_id,controller=interruption_handling_properties['controller-id'])
    logger.info(info_message)
    return(info_message)