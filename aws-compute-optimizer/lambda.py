import boto3

def handler(event, context):

  client = boto3.client('compute-optimizer')
              
  response = client.get_auto_scaling_group_recommendations(
  )
  print(response)
  
  client = boto3.client('ssm')

  response = client.put_parameter(
    Name='computeOptimizer1',
    Value='c3.large',
    Type='String',
    Overwrite=True
  )
  print(response)

  response = client.put_parameter(
    Name='computeOptimizer2',
    Value='c4.large',
    Type='String',
    Overwrite=True
  )
  print(response)

  response = client.put_parameter(
    Name='computeOptimizer3',
    Value='c5.large',
    Type='String',
    Overwrite=True
  )
  print(response)

  client = boto3.client('cloudformation')
  #response = client.update_stack(
  #  StackName='opt4',
  #  UsePreviousTemplate=True,
  #  Capabilities=[
  #      'CAPABILITY_IAM'
  #  ]
  #)
  print(response)
  
return
