#!/bin/bash

if [ "$1" == "" ]; then

  REGIONS=$(aws ec2 describe-regions | jq -r '.Regions[].RegionName')

  for region in $REGIONS
    do
		  AMI=$(aws ec2 describe-images \
		    --region $region \
		    --owners amazon \
		    --filters 'Name=name,Values=amzn2-ami-hvm-2.0.????????-x86_64-gp2' 'Name=state,Values=available' \
		    --output json | \
		    jq -r '.Images | sort_by(.CreationDate) | last(.[]).ImageId')
		  echo -e "    $region: {AMI: $AMI}"
    done

else
  AMI=$(aws ec2 describe-images \
    --region $1 \
    --owners amazon \
    --filters 'Name=name,Values=amzn2-ami-hvm-2.0.????????-x86_64-gp2' 'Name=state,Values=available' \
    --output json | \
    jq -r '.Images | sort_by(.CreationDate) | last(.[]).ImageId')
  echo -e "$1: {AMI: $AMI}"
fi