#!/bin/bash

date
echo "BEGIN"
env
echo
echo "jobId: $AWS_BATCH_JOB_ID"
echo "jobQueue: $AWS_BATCH_JQ_NAME"
echo "computeEnvironment: $AWS_BATCH_CE_NAME"
echo "batchjobarrayindex: $AWS_BATCH_JOB_ARRAY_INDEX"
echo "region:" $REGION
echo "s3bucket:" $S3BUCKET
echo "input:" $INPUT
echo
FNAME=$(echo $AWS_BATCH_JOB_ARRAY_INDEX-$INPUT | rev | cut -f2 -d"." | rev | tr '[:upper:]' '[:lower:]')
echo "fname:" $FNAME
aws s3 cp s3://$S3BUCKET/$AWS_BATCH_JOB_ARRAY_INDEX-$INPUT /tmp --region $REGION
convert /tmp/$AWS_BATCH_JOB_ARRAY_INDEX-$INPUT /tmp/$FNAME.pdf
aws s3 cp /tmp/$FNAME.pdf s3://$S3BUCKET --region $REGION
rm -f /tmp/$AWS_BATCH_JOB_ARRAY_INDEX-$INPUT /tmp/$FNAME.pdf
date
echo "END"