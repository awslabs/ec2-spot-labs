#!/bin/bash

while sleep 5; do
  if [ -z $(curl -Isf http://169.254.169.254/latest/meta-data/spot/instance-action) ];
  then
    /bin/false
  else
    logger "[$0]: spot instance interruption notice detected"

    # take whatever action necessary to handle interruption here...

    logger "[$0]: putting myself to sleep..."
    sleep 120
  fi
done
