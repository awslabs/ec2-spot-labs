#!/bin/bash

# Copyright 2021, AWS (https://github.com/awslabs/ec2-spot-labs/blob/master/LICENSE.txt)
# Written by Steve Cole

########################################
#
# version 0.0.1 - first
# - create iam policy
# - create iam role
# - set trust relationship
#
########################################

DEBUG=false

# Transform long options to short ones
# (these are common pass-throughs for the CLI)
#
for arg in "$@"; do
  shift
  case "$arg" in
    "--profile") set -- "$@" "-p" ;;
    *)           set -- "$@" "$arg"
  esac
done

# parse short options
#
while getopts “dp:n:” opt; do
  case $opt in
    d) DEBUG=true ;;
    n) NAME=$OPTARG ;;
    p) PROFILE=$OPTARG ;;
  esac
done

########################################
# multi-use functions
########################################

# state file(s)
#
OUT='create-iam.out'
JSON='create-iam.json'

# standardized exit
#
function exitWithError {

    echo $1
    exit

}

# usage synopsis
#
function usage {
    echo
    echo $1
    echo "Usage: $0"
    echo "       -n name"
    echo "       [--profile <profile>]"
    echo 
    exit
}

########################################
# single-use functions
########################################

# This is the part where we kick you for failing to include instance ID or IAM role
#
function checkRequiredArgs {

    # TODO require instance ID
    # TODO require IAM role
    [ -z $NAME ] && usage "IAM role/policy is required"

}

# create the policy in advance to attach to the role
# (we need to capture the returned ARN here)
#
function createPolicy {

    echo -n "Creating policy... "

cat <<- EOF > $JSON
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowFISExperimentRoleReadOnly",
            "Effect": "Allow",
            "Action": "ec2:DescribeInstances",
            "Resource": "*"
        },
        {
            "Sid": "AllowFISExperimentRoleEC2Actions",
            "Effect": "Allow",
            "Action": "ec2:SendSpotInstanceInterruptions",
            "Resource": "arn:aws:ec2:*:*:instance/*"
        }
    ]
}
EOF

    aws iam create-policy --policy-name $NAME --policy-document file://$JSON > $OUT
    [ $? -ne 0 ] && exitWithError "failed to create policy"

    POLICY_ARN=$(grep "arn:aws:iam" $OUT | awk -F '"' '{ print $4 '})

    echo OK

}

# create the role, and with it a trust relationship for fis
#
function createRole {

cat <<- EOF > $JSON
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "fis.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

    echo -n "Creating role... "

    aws iam create-role --role-name $NAME --assume-role-policy-document file://$JSON > $OUT
    [ $? -ne 0 ] && exitWithError "failed to create role"

    echo OK

}

# attach our policy to our role
#
function attachPolicy {

    echo -n "Attaching policy... "

    aws iam attach-role-policy --role-name $NAME --policy-arn $POLICY_ARN > $OUT
    [ $? -ne 0 ] && exitWithError "failed to attach policy"

    echo OK

}

# remove state files from disk
#
function cleanup {
  rm $JSON
  rm $OUT
}

checkRequiredArgs
createPolicy
createRole
attachPolicy
cleanup