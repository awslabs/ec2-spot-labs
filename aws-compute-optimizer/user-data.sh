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
sed -i "s|%CLOUDWATCHLOGSGROUP%|$CLOUDWATCHLOGSGROUP|g" /etc/awslogs/awslogs.conf
systemctl enable awslogsd.service
systemctl start awslogsd.service

rpm -Uvh https://s3.amazonaws.com/amazoncloudwatch-agent/amazon_linux/amd64/latest/amazon-cloudwatch-agent.rpm
cp -av $WORKING_DIR/config.json /opt/aws/amazon-cloudwatch-agent/bin/
mkdir -p /usr/share/collectd/
touch /usr/share/collectd/types.db
systemctl enable amazon-cloudwatch-agent.service
/opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a fetch-config -m ec2 -c file:/opt/aws/amazon-cloudwatch-agent/bin/config.json -s

cat >/etc/cron.hourly/stress.sh <<EOF
#!/bin/bash

perl -le 'sleep rand 900'
stress-ng --matrix 0 -t 30m
EOF

chmod +x /etc/cron.hourly/stress.sh








