#!/bin/bash
set -e

# Execute commands $1 seconds or 30 seconds time before execution
execute_secs_before_termination=${1:-30}

# Look for Instance metadata interruption notice
while [ -n "$(curl -s http://169.254.169.254/latest/meta-data/spot/instance-action | grep 404)" ]; 
do 
   sleep 2 
done

termination_time=$(date -d $(curl -s http://169.254.169.254/latest/meta-data/spot/instance-action | jq -r .time) +%s)
current_time=$(date +%s)
time_to_termination=$(expr $termination_time - $current_time)

echo "Current time is: $(date +'%Y-%m-%d %H:%M:%S')"
echo "Spot Instance termination time is: $(date -d @$termination_time +'%Y-%m-%d %H:%M:%S')"


if [ $time_to_termination -ge $execute_secs_before_termination ]; 
then
   wait_time=$(expr $time_to_termination - $execute_secs_before_termination)
   echo "Waiting $wait_time seconds before executing termination commands "  
   sleep $wait_time
fi

echo "$(date +'%Y-%m-%d %H:%M:%S'): Wait script finished."
