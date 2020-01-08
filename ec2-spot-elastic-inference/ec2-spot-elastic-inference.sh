#!/bin/bash -x

echo "Hello World from EC2 Spot Team..."
#Global Defaults
DEFAULT_REGION=us-east-1
SLEEP=5
LAUNCH_TEMPLATE_NAME=EC2SpotElasticInference-LT
LAUNCH_TEMPLATE_VERSION=1
CFS_STACK_NAME=EI-Spot-Stack
CFS_STACK_FILE=EI_Spot_CFN.yaml
declare -a CFK_STACK_OP_KEYS_LIST=("awsRegionId"  "eventRule" "instanceProfile" 
                                    "instanceRole" "instanceSecurityGroup" "publicSubnet" 
                                    "snsTopic" "vpc" "vpcEndpoint" )



cp -Rfp templates/*.json .
cp -Rfp templates/*txt .

#CFS_STACK_ID=$(aws cloudformation create-stack --stack-name $CFS_STACK_NAME  --template-body file://$CFS_STACK_FILE --capabilities CAPABILITY_IAM --region $DEFAULT_REGION|jq -r '.StackId')
echo "Created the stack $CFS_STACK_NAME with Stack Id $CFS_STACK_ID. Please wait till the status is COMPLETE"

aws cloudformation wait stack-create-complete --stack-name $CFS_STACK_NAME --no-paginate


for CFK_STACK_OP_KEY in "${CFK_STACK_OP_KEYS_LIST[@]}"; do
    CFK_STACK_OP_VALUE=$(aws cloudformation describe-stacks --stack-name $CFS_STACK_NAME | jq -r ".Stacks[].Outputs[]| select(.OutputKey==\"$CFK_STACK_OP_KEY\")|.OutputValue")
    echo "$CFK_STACK_OP_KEY=$CFK_STACK_OP_VALUE"
    #sed -i.bak -e "s#%$CFK_STACK_OP_KEY%#$CFK_STACK_OP_VALUE#g"  user-data.txt
    sed -i.bak -e "s#%$CFK_STACK_OP_KEY%#$CFK_STACK_OP_VALUE#g"  EI_launch_template.json
done

export AMI_ID=$(aws ec2 describe-images --owners amazon --filters 'Name=name,Values=Deep Learning AMI (Amazon Linux 2) Version*' 'Name=state,Values=available' --output json | jq -r '.Images |   sort_by(.CreationDate) | last(.[]).ImageId')
echo "Amazon AMI_ID is $AMI_ID"

sed -i.bak  -e "s#%ami-id%#$ami_id#g"  EI_launch_template.json

LAUCH_TEMPLATE_ID=$(aws ec2 create-launch-template --launch-template-name $LAUNCH_TEMPLATE_NAME --version-description LAUNCH_TEMPLATE_VERSION --launch-template-data file://EI_launch_template.json | jq -r '.LaunchTemplate.LaunchTemplateId')
#LAUCH_TEMPLATE_ID=lt-046437183d3b6bf53
echo "Amazon LAUCH_TEMPLATE_ID is $LAUCH_TEMPLATE_ID"

exit 0

sleep 5


if [ "1" == "2" ]; then

    
RDS_ID=$(aws rds create-db-instance --cli-input-json file://rds.json|jq -r '.DBInstance.DBInstanceIdentifier')
echo "Amazon RDS_ID is $RDS_ID"

aws rds wait  db-instance-available --db-instance-identifier $RDS_ID

export AMI_ID=$(aws ec2 describe-images --owners amazon --filters 'Name=name,Values=Deep Learning AMI (Amazon Linux 2) Version*' 'Name=state,Values=available' --output json | jq -r '.Images |   sort_by(.CreationDate) | last(.[]).ImageId')
echo "Amazon AMI_ID is $AMI_ID"


sed -i.bak  -e "s#%ami-id%#$ami_id#g" -e "s#%UserData%#$(cat user-data.txt | base64 --wrap=0)#g" launch-template-data.json

LAUCH_TEMPLATE_ID=$(aws ec2 create-launch-template --launch-template-name $LAUNCH_TEMPLATE_NAME --version-description LAUNCH_TEMPLATE_VERSION --launch-template-data file://launch-template-data.json | jq -r '.LaunchTemplate.LaunchTemplateId')
#LAUCH_TEMPLATE_ID=lt-046437183d3b6bf53
echo "Amazon LAUCH_TEMPLATE_ID is $LAUCH_TEMPLATE_ID"


aws elbv2 create-load-balancer --cli-input-json file://application-load-balancer.json
alb_arn=$(aws elbv2 describe-load-balancers --names runningAmazonEC2WorkloadsAtScale --query LoadBalancers[].LoadBalancerArn --output text)

aws elbv2 create-target-group --cli-input-json file://target-group.json
tg_arn=$(aws elbv2 describe-target-groups --names runningAmazonEC2WorkloadsAtScale --query TargetGroups[].TargetGroupArn --output text)

sed -i.bak -e "s#%TargetGroupArn%#$tg_arn#g" modify-target-group.json
aws elbv2 modify-target-group-attributes --cli-input-json file://modify-target-group.json

sed -i.bak -e "s#%LoadBalancerArn%#$alb_arn#g" -e "s#%TargetGroupArn%#$tg_arn#g" listener.json

aws elbv2 create-listener --cli-input-json file://listener.json

sed -i.bak -e "s#%TargetGroupARN%#$tg_arn#g" asg.json

aws autoscaling create-auto-scaling-group --cli-input-json file://asg.json


# Grab the RDS endpoint
rds_endpoint=$(aws rds describe-db-instances --db-instance-identifier runningamazonec2workloadsatscale --query DBInstances[].Endpoint.Address --output text)

#mysql -h $rds_endpoint -u dbadmin --password=db-pass-2020 -f koel < koel.sql

sed -i.bak -e "s#%endpoint%#$rds_endpoint#g" codedeploy/scripts/configure_db.sh

git clone https://github.com/phanan/koel.git
    
cd koel && git checkout v3.7.2
cp -avr ../codedeploy/* .
aws deploy create-application --application-name koelApp

aws deploy push --application-name koelApp --s3-location s3://$code_deploy_bucket/koelApp.zip --no-ignore-hidden-files
cd ..
aws deploy create-deployment-group --cli-input-json file://deployment-group.json
aws deploy create-deployment --cli-input-json file://deployment.json


mkdir -p ~/environment/media

sudo mount -t efs $file_system:/ ~/environment/media
    
sudo chown ec2-user. ~/environment/media
    
sudo cp -av *.mp3 ~/environment/media

aws autoscaling put-scaling-policy --cli-input-json file://asg-automatic-scaling.json

fi
