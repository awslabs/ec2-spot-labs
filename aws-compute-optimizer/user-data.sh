#!/bin/bash

INSTANCE_ID=$(curl -s http://169.254.169.254/latest/meta-data/instance-id)
WORKING_DIR=/root/ec2-spot-labs/aws-compute-optimizer

yum -y --security update

amazon-linux-extras install epel

yum -y update aws-cli

yum -y install \
  awslogs jq stress-ng

aws configure set default.region $REGION

cp -av $WORKING_DIR/awslogs.conf /etc/awslogs/

sed -i "s|us-east-1|$REGION|g" /etc/awslogs/awscli.conf
sed -i "s|%CLOUDWATCHLOGSGROUP%|$CLOUDWATCHLOGSGROUP|g" /etc/awslogs/awslogs.conf

chkconfig awslogs on && service awslogs restart

