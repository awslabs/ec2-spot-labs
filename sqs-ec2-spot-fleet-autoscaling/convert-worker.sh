#!/bin/bash

REGION=%REGION%
S3BUCKET=%S3BUCKET%
SQSQUEUE=%SQSQUEUE%

while sleep 5; do 

  JSON=$(aws sqs --output=json get-queue-attributes \
    --queue-url $SQSQUEUE \
    --attribute-names ApproximateNumberOfMessages)
  MESSAGES=$(echo "$JSON" | jq -r '.Attributes.ApproximateNumberOfMessages')

  if [ $MESSAGES -eq 0 ]; then

    continue

  fi

  JSON=$(aws sqs --output=json receive-message --queue-url $SQSQUEUE)
  RECEIPT=$(echo "$JSON" | jq -r '.Messages[] | .ReceiptHandle')
  BODY=$(echo "$JSON" | jq -r '.Messages[] | .Body')

  if [ -z "$RECEIPT" ]; then

    logger "$0: Empty receipt. Something went wrong."
    continue

  fi

  logger "$0: Found $MESSAGES messages in $SQSQUEUE. Details: JSON=$JSON, RECEIPT=$RECEIPT, BODY=$BODY"

  INPUT=$(echo "$BODY" | jq -r '.Records[0] | .s3.object.key')
  FNAME=$(echo $INPUT | rev | cut -f2 -d"." | rev | tr '[:upper:]' '[:lower:]')
  FEXT=$(echo $INPUT | rev | cut -f1 -d"." | rev | tr '[:upper:]' '[:lower:]')

  if [ "$FEXT" = "jpg" -o "$FEXT" = "png" -o "$FEXT" = "gif" ]; then

    logger "$0: Found work to convert. Details: INPUT=$INPUT, FNAME=$FNAME, FEXT=$FEXT"

    aws s3 cp s3://$S3BUCKET/$INPUT /tmp

    convert /tmp/$INPUT /tmp/$FNAME.pdf

    logger "$0: Convert done. Copying to S3 and cleaning up"

    aws s3 cp /tmp/$FNAME.pdf s3://$S3BUCKET

    rm -f /tmp/$INPUT /tmp/$FNAME.pdf

    aws sqs --output=json delete-message --queue-url $SQSQUEUE --receipt-handle $RECEIPT

  else

    logger "$0: Skipping message - file not of type jpg, png, or gif. Deleting message from queue"

    aws sqs --output=json delete-message --queue-url $SQSQUEUE --receipt-handle $RECEIPT

  fi

done