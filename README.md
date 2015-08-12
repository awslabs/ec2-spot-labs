aws-spot-labs
=============

**aws-spot-labs** is a collection of code examples and scripts that illustrates some of the Best Practices in using [AWS Spot Instances](https://aws.amazon.com/ec2/purchasing-options/spot-instances/)



get_spot_duration.py
--------------------
**get_spot_duration.py** helps find capacity pools (defined as instance type and AZ) with lower price volatility by ordering these pools based on duration of time since the Spot price last exceeded the bid price. It uses [AWS CLI](https://aws.amazon.com/cli/) to programmatically obtain Spot price history data.
 
Input: 
* AWS EC2 region
* product-description
* combination of instance types and Spot bids prices for each instance type.

For example, for c3 family and bids equal to 50% of [On-demand price](https://aws.amazon.com/ec2/pricing/):
```
bash-3.2$ python get_spot_duration.py \
--region us-east-1 \
--product-description 'Linux/UNIX' \
--bids c3.large:0.05,c3.xlarge:0.105,c3.2xlarge:0.21,c3.4xlarge:0.42,c3.8xlarge:0.84 


Duration        Instance Type   Availability Zone
168.0   c3.8xlarge      us-east-1a
168.0   c3.8xlarge      us-east-1d
168.0   c3.8xlarge      us-east-1e
168.0   c3.4xlarge      us-east-1b
168.0   c3.4xlarge      us-east-1d
168.0   c3.4xlarge      us-east-1e
168.0   c3.xlarge       us-east-1d
168.0   c3.xlarge       us-east-1e
168.0   c3.large        us-east-1b
168.0   c3.large        us-east-1d
168.0   c3.large        us-east-1e
168.0   c3.2xlarge      us-east-1b
168.0   c3.2xlarge      us-east-1e
117.7   c3.large        us-east-1a
36.1    c3.2xlarge      us-east-1d
34.5    c3.4xlarge      us-east-1a
23.0    c3.xlarge       us-east-1b
21.9    c3.2xlarge      us-east-1a
17.3    c3.8xlarge      us-east-1b
0.1     c3.xlarge       us-east-1a
```

Notes:

* Availability Zone mapping may be different for different AWS accounts
* 168.0 means that Spot price hasn't exceeded specified bid during last week (168 hours by default) 
* Actual numbers will be different, script uses last 1-week of price history and Spot prices change continiously based on supply and demand
* Newer accounts that are VPC by default  may not see all purchase options and only see ( "Linux/UNIX", "SUSE Linux", "Windows" )

Please see **get_spot_duration.py --help** for additional options.

Issues
======

Please address any issues or feedback to dpush at amazon dot com
