1. Create launch template

aws ec2 create-launch-template --cli-input-json file://ec2-fleet-launch-template.json

2. Create EC2 Fleet with baseline On-Demand

aws ec2 create-fleet --cli-input-json file://ec2-fleet-ec2-spot-turbo-boost.json

2a. Describe Fleet

aws ec2 describe-fleets --fleet-id $FLEETID

2b. Describe Fleet history

aws ec2 describe-fleet-history --fleet-id $FLEETID --start-time 2018-07-01

2c. Turbo boost EC2 Fleet with Spot

aws ec2 modify-fleet --fleet-id $FLEETID --target-capacity-specification TotalTargetCapacity=20

2b. Clean up

aws ec2 delete-fleets --fleet-id $FLEETID --terminate-instances

3. Create EC2 Fleet with million core scale and On-Demand backup

aws ec2 create-fleet --cli-input-json file://ec2-fleet-on-demand-backup.json

3a. Describe Fleet

aws ec2 describe-fleets --fleet-id $FLEETID

3b. Describe Fleet history

aws ec2 describe-fleet-history --fleet-id $FLEETID --start-time 2018-07-01

3c. Clean up

aws ec2 delete-fleets --fleet-id $FLEETID --terminate-instances

4. Create EC2 Fleet with weighted capacity (vCPUs)

aws ec2 create-fleet --cli-input-json file://ec2-fleet-ec2-spot-weighted-capacity.json

4a. Describe Fleet

aws ec2 describe-fleets --fleet-id $FLEETID

4b. Describe Fleet history

aws ec2 describe-fleet-history --fleet-id $FLEETID --start-time 2018-07-01

4c. Clean up

aws ec2 delete-fleets --fleet-id $FLEETID --terminate-instances
