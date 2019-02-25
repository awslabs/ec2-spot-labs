# ecs-spot-agent

If you want to use [EC2 Spot Instances](https://aws.amazon.com/ec2/spot/) with [ECS](https://aws.amazon.com/ecs/), you need to care for termination-time.
ecs-spot-agent can check termination-time and deregister ECS instance from ECS Cluster.

## Requirement

LaunchType: EC2
NetworkMode: host

## How to Use

If you use ecs-spot-agent quickly, please use [CloudFormation Template](https://github.com/mats16/ec2-spot-labs/tree/master/ecs-spot-agent/ecs-spot-agent.yaml).
You only need to choose a target ECS cluster.
