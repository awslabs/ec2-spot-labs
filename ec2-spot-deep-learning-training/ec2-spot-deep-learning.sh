#!/bin/bash -x

echo "Hello World from EC2 Spot Team..."
#Global Defaults
DEFAULT_REGION=us-east-1
SLEEP=5
LAUNCH_TEMPLATE_NAME=EC2SpotElasticInference-LT
LAUNCH_TEMPLATE_VERSION=1
CFS_STACK_NAME=EI-Spot-Stack
CFS_STACK_FILE=EI_Spot_CFN.yaml

MAC=$(curl -s http://169.254.169.254/latest/meta-data/mac)
INSTANCE_ID=$(curl -s http://169.254.169.254/latest/meta-data/instance-id)
PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)
AWS_AVAIALABILITY_ZONE=$(curl -s 169.254.169.254/latest/dynamic/instance-identity/document | jq -r '.availabilityZone')
AWS_REGION=$(curl -s 169.254.169.254/latest/dynamic/instance-identity/document | jq -r '.region')
INTERFACE_ID=$(curl -s http://169.254.169.254/latest/meta-data/network/interfaces/macs/$MAC/interface-id)



SECURITY_GROUP_ID=sg-4f3f0d1e
SUBNET_ID=subnet-764d7d11
KEYPAIR_NAME=awsajp_keypair
AMI_ID=ami-02bd97932dabc037b

EBS_TYPE=gp2
EBS_SIZE=100
EBS_DEV=/dev/xvdb
MOUNT_POINT=/dltraining

cp -Rfp templates/*.json .
cp -Rfp templates/*txt .

if [[ "1" == "2" ]]; then
INSTANCE_ID=$(aws ec2 run-instances \
    --image-id $AMI_ID \
    --security-group-ids $SECURITY_GROUP_ID \
    --count 1 \
    --instance-type m4.xlarge \
    --key-name $KEYPAIR_NAME \
    --subnet-id $SUBNET_ID \
    --query "Instances[0].InstanceId")
    
echo "INSTANCE_ID is $INSTANCE_ID"

aws ec2 wait instance-running \
    --instance-ids $INSTANCE_ID

SECONDARY_VOLUME_ID=$(aws ec2 create-volume \
      --region $AWS_REGION \
      --volume-type $EBS_TYPE \
      --size $EBS_SIZE  \
      --availability-zone $AWS_AVAIALABILITY_ZONE \
      --tag-specifications 'ResourceType=volume,Tags=[{Key=Name,Value=DL-datasets-checkpoints}]' \
      | jq -r '.VolumeId')
echo "SECONDARY_VOLUME_ID=$SECONDARY_VOLUME_ID"

fi

SECONDARY_VOLUME_ID=vol-0ef9b31ca0c5c169f

aws ec2 wait volume-available  --volume-ids $SECONDARY_VOLUME_ID

aws ec2 attach-volume --volume-id $SECONDARY_VOLUME_ID \
    --instance-id $INSTANCE_ID \
    --device $EBS_DEV

sleep 15
    
sudo mkdir $MOUNT_POINT
sudo mkfs -t xfs $EBS_DEV
sudo mount $EBS_DEV $MOUNT_POINT
cd $MOUNT_POINT
mkdir datasets
mkdir checkpoints


   umount $MOUNT_POINT
   yum -y removed httpd
   rm -rf /var/www/
   aws ec2 detach-volume --volume-id $SECONDARY_VOLUME_ID



         
         
         
    

exit 0

