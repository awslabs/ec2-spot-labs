
#!/bin/bash

#aws ec2 describe-spot-instance-requests --filters "Name=instance-id,Values=i-006734de2bece0c91"

#SIR=$(aws ec2 describe-instances --instance-ids i-006734de2bece0c91 --query 'Reservations[*].Instances[*].SpotInstanceRequestId' --output text)

instanceId=$(curl http://169.254.169.254/latest/meta-data/instance-id)

spotPrice=$(aws ec2 describe-spot-instance-requests --filters "Name=instance-id,Values=$instanceId" | jq -r '.SpotInstanceRequests[].SpotPrice')

instanceType=$(aws ec2 describe-spot-instance-requests --filters "Name=instance-id,Values=$instanceId" | jq -r '.SpotInstanceRequests[].LaunchSpecification.InstanceType')

launchedAvailabilityZone=$(aws ec2 describe-spot-instance-requests --filters "Name=instance-id,Values=$instanceId" | jq -r '.SpotInstanceRequests[].LaunchedAvailabilityZone')

productDescription=$(aws ec2 describe-spot-instance-requests --filters "Name=instance-id,Values=$instanceId" | jq -r '.SpotInstanceRequests[].ProductDescription')

timeStamp=$(date -u "+%FT%T")

currentSpotPrice=$(aws ec2 describe-spot-price-history --availability-zone $launchedAvailabilityZone --instance-types $instanceType --product-description $productDescription --start-time $timeStamp --end-time $timeStamp | jq -r '.SpotPriceHistory[].SpotPrice')


