#!/usr/bin/env python3

from aws_cdk import (
  aws_ec2 as ec2,
  aws_iam as iam,
  aws-autoscaling as autoscaling,
  core
)

class ec2SpotAsgStack(core.Stack):
  def __init__(self, app: core.App, id: str) -> None:
    super().__init__(app, id)

    vpc = ec2.Vpc(
      self,
      "VPC",
      max_azs = 2
    )

    instanceSecurityGroup = ec2.SecurityGroup(
      self,
      "INSTANCESECURITYGROUP",
      vpc = vpc
      )

    loadBalancerSecurityGroup = ec2.SecurityGroup(
      self,
      "LOADBALANCERSECURITYGROUP",
      vpc = vpc
      )

    connection = ec2.Connections(
      default_port = ec2.Port.tcp(80),
      security_groups = [
        instanceSecurityGroup,
        loadBalancerSecurityGroup
        ]
      )

    connection.allow_default_port_internally()
    connection.allow_default_port_from_any_ipv4()

    instanceRole = iam.Role(
      self,
      "INSTANCEROLE",
      assumed_by = iam.ServicePrincipal('ec2.amazonaws.com'),
      managed_policies = [
        iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AmazonEC2RoleforSSM")
        ]
      )

    instanceProfile = iam.CfnInstanceProfile(
      self,
      "INSTANCEPROFILE",
      roles = [
        instanceRole.role_name
        ]
      )
    
    core.CfnOutput(
      self,
      "vpc",
      value = vpc.vpc_id
      )

    core.CfnOutput(
      self,
      "publicSubnet1",
      value = vpc.public_subnets[0].subnet_id
      )

    core.CfnOutput(
      self,
      "publicSubnet2",
      value = vpc.public_subnets[1].subnet_id
      )

    core.CfnOutput(
      self,
      "instanceSecurityGroup",
      value = instanceSecurityGroup.security_group_name
      )

    core.CfnOutput(
      self,
      "loadBalancerSecurityGroup",
      value = loadBalancerSecurityGroup.security_group_name
      )

    core.CfnOutput(
      self,
      "instanceProfile",
      value = instanceProfile.attr_arn
      )

app = core.App()
ec2SpotAsgStack(app, "ec2SpotAsgStack")
app.synth()