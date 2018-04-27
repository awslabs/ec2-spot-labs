import boto3
def handler(event, context):
  instanceId = event['detail']['instance-id']
  instanceAction = event['detail']['instance-action']
  try:
    ec2client = boto3.client('ec2')
    describeTags = ec2client.describe_tags(Filters=[{'Name': 'resource-id','Values':[instanceId],'Name':'key','Values':['loadBalancerTargetGroup']}])
    print(describeTags['Tags'][0]['Value'])
  except:
    print("No action being taken. Unable to describe tags for instance id:", instanceId)
    return
  try:
    elbv2client = boto3.client('elbv2')
    deregisterTargets = elbv2client.deregister_targets(TargetGroupArn=describeTags['Tags'][0]['Value'],Targets=[{'Id':instanceId}])
    print(deregisterTargets)
  except:
    print("No action being taken. Unable to deregister targets for instance id:", instanceId)
    return
  return
