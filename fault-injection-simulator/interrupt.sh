#!/bin/bash

# Copyright 2021, AWS (https://github.com/awslabs/ec2-spot-labs/blob/master/LICENSE.txt)
# Written by Steve Cole

########################################
#
# version 0.0.1 - first
# - create experiment template
# - run experiment
# - delete experiment template
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
    "--region")  set -- "$@" "-w" ;;
    *)           set -- "$@" "$arg"
  esac
done

# parse short options
#
while getopts “di:m:p:r:w:” opt; do
  case $opt in
    d) DEBUG=true ;;
    i) INSTANCE=$OPTARG ;;
    r) IAM_ROLE=$OPTARG ;;
    m) MINUTES=$OPTARG ;;
    p) PROFILE=$OPTARG ;;
    w) REGION=$OPTARG ;;
  esac
done

# Set a default of 2 for unspecified minutes
#
[ -z $MINUTES ] && MINUTES=2

$DEBUG && echo ">> debug mode"

# debug vars
#
$DEBUG && [ ! -z $INSTANCE ] && echo instance: $INSTANCE
$DEBUG && [ ! -z $IAM_ROLE ] && echo role:     $IAM_ROLE
$DEBUG && [ ! -z $MINUTES ]  && echo minutes:  $MINUTES
$DEBUG && [ ! -z $PROFILE ]  && echo profile:  $PROFILE
$DEBUG && [ ! -z $REGION ]   && echo region:   $REGION

# consolidate AWS args; python doesn't like extra spaces
#
[ -z "$PROFILE" ] || PROFILE="--profile $PROFILE"
[ -z "$REGION" ] || REGION="--region $REGION"

[ ! -z "$PROFILE" ] || [ ! -z "$REGION" ] && AWS_ARGS=$(echo "$PROFILE $REGION" | xargs)

# state files
#
JSON=$(mktemp -t 'interrupt.XXXX.json')
OUT=$(mktemp -t 'interrupt.XXXX.out')
ERR=$(mktemp -t 'interrupt.XXXX.err')

########################################
# multi-use functions
########################################

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
    echo "       -i <instance-id>"
    echo "       -r <role>"
    echo "       [-m <minutes>]"
    echo "       [--profile <profile>]"
    echo "       [--region <region>]"
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
    [ -z $INSTANCE ] && usage "instance-id is required"
    [ -z $IAM_ROLE ] && usage "IAM role is required"
}

# little known trick to figure out your IAM user (or role)
# also handy for getting account numbers (which we need)
#
function whoAmI {

    echo -n "Checking connection to AWS... "

    aws $AWS_ARGS sts get-caller-identity > $OUT
    ACCOUNT=$(grep "\"Account\"": $OUT | awk -F '"' '{ print $4 }')
    [ $? -ne 0 ] && exitWithError "not connected"
    [ -z $ACCOUNT ] && exitWithError "couldn't find account ID"

    echo OK
}

# checking policies would be quite involved; we'll error if insufficient
#
function checkRole {

    echo -n "Checking for IAM Role... "

    aws $AWS_ARGS iam get-role --role-name $IAM_ROLE > $OUT 2>$ERR
    [ $? -ne 0 ] && exitWithError "could not find $IAM_ROLE"

    echo OK
}

# minimal FIS experiment template
#
function createExperimentTemplate {

  echo -n "Creating FIS experiment template... "

cat <<- EOF > $JSON
{
    "description": "spotInterruption",
    "stopConditions": [
        {
            "source": "none"
        }
    ],
    "targets": {
        "spotInstance": {
            "resourceType": "aws:ec2:spot-instance",
            "resourceArns": [
                "arn:aws:ec2:$REGION:$ACCOUNT:instance/$INSTANCE"
            ],
            "selectionMode": "ALL"
        }
    },
    "actions": {
        "interrupt": {
            "actionId": "aws:ec2:send-spot-instance-interruptions",
            "description": "spotInterruption",
            "parameters": {
                "durationBeforeInterruption": "PT${MINUTES}M"            },
            "targets": {
                "SpotInstances": "spotInstance"
            }
        }
    },
    "roleArn": "arn:aws:iam::$ACCOUNT:role/$IAM_ROLE",
    "tags": {
        "Name": "spotInterruption"
    }
}
EOF

    aws $AWS_ARGS fis create-experiment-template --cli-input-json file://$JSON > $OUT
    [ $? -ne 0 ] && exitWithError "failed to create "

    echo OK
}

# start the experiment
#
function startExperiment {

    echo -n "Starting experiment... "

    TEMPLATE_ID=$(grep "\"id\"": $OUT | awk -F '"' '{ print $4 }')
    aws $AWS_ARGS fis start-experiment --experiment-template-id $TEMPLATE_ID > $OUT
    [ $? -ne 0 ] && exitWithError "failed to start"

    echo OK

}

# the moving part people like to see in scripts
#
function getExperiment {

    echo "Watching experiment status... "

    STATUS=''
    EXPERIMENT_ID=$(grep "\"id\"": $OUT | awk -F '"' '{ print $4 }')

    while true ; do

        aws $AWS_ARGS fis get-experiment --id $EXPERIMENT_ID > $OUT
        [ $? -ne 0 ] && exitWithError "failed to get experiment"
        STATUS=$(grep reason $OUT | grep -i experiment | awk -F '"' '{ print $4 }')
        echo "($EXPERIMENT_ID) $STATUS"
        if [ "$STATUS" = "Experiment completed." ]; then
            break
        fi

        # if there's an error (like not including the correct region)
        ERROR=$(grep reason $OUT | grep -i error | wc -l)
        if [ $ERROR -gt 0 ]; then
            echo "($EXPERIMENT_ID) Experiment failed."
            break
        fi
        sleep 5

    done

}

# clean up after ourselves (a la cloud formation rewind)
#
function deleteExperimentTemplate {

    echo -n "Deleting experiment template... "

    aws $AWS_ARGS fis delete-experiment-template --id $TEMPLATE_ID > $OUT
    [ $? -ne 0 ] && exitWithError "failed to delete"

    echo OK
  
}

# remove state files from disk
#
function cleanup {
  rm $JSON
  rm $OUT
  rm $ERR
}


########################################
# main
########################################

checkRequiredArgs
whoAmI
checkRole
# ...and blindly assume we have permissions to do what we need
# (not ideal, but IAM CLI is a booger)
# (also, this is where admin privileges would be nice)
createExperimentTemplate
startExperiment
getExperiment
deleteExperimentTemplate
cleanup
