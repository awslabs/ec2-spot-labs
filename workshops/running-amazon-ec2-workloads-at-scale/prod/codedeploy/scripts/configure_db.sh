#!/bin/bash

sed -i 's/DB_HOST=127.0.0.1/DB_HOST=runningamazonec2workloadsatscale.ckhifpaueqm7.us-east-1.rds.amazonaws.com/g' /var/www/koel/.env
