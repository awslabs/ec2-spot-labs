locals {
  name        = "ecs-spot"
  cluster_name = "${local.name}-cluster-${uuid()}"
}
data "aws_vpc" "default" {
  default = true
}

data "aws_subnet_ids" "subnets" {
  vpc_id = data.aws_vpc.default.id
}

data "aws_ami" "amazon_linux2_ecs" {
  most_recent = true

  owners = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-ecs-hvm-*-x86_64-ebs"]
  }

  filter {
    name   = "owner-alias"
    values = ["amazon"]
  }
}


#---------------------------------------------------
## add user data to launch template
locals {
  user_data =<<-EOF
    #!/bin/bash
    echo ECS_CLUSTER=${local.cluster_name} >> /etc/ecs/ecs.config;echo ECS_BACKEND_HOST= >> /etc/ecs/ecs.config;echo ECS_ENABLE_SPOT_INSTANCE_DRAINING=true>>/etc/ecs/ecs.config;
    EOF
}
resource "aws_iam_role" "ecs_instance_role" {
    name                = "ecs-instance-role"
    path                = "/"
    assume_role_policy  = data.aws_iam_policy_document.ecs_instance_policy.json
}

data "aws_iam_policy_document" "ecs_instance_policy" {
    statement {
        actions = ["sts:AssumeRole"]

        principals {
            type        = "Service"
            identifiers = ["ec2.amazonaws.com"]
        }
    }
}

resource "aws_iam_role_policy_attachment" "ecs_instance_role_attachment" {
    role       = aws_iam_role.ecs_instance_role.name
    policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonEC2ContainerServiceforEC2Role"
}

resource "aws_iam_instance_profile" "ecs_instance_profile" {
    name = "ecs-instance-profile"
    role = aws_iam_role.ecs_instance_role.id
}
resource "aws_launch_template" "ecs_lt" {
  name = "lt-${local.cluster_name}"
  image_id = data.aws_ami.amazon_linux2_ecs.id
  user_data = base64encode(local.user_data)

  iam_instance_profile {
    name = aws_iam_instance_profile.ecs_instance_profile.name
  }
}
#----------------------------------------------------
resource "aws_autoscaling_group" "ecs_spot_asg" {
  name = "${local.name}-spot-asg"

  vpc_zone_identifier = data.aws_subnet_ids.subnets.ids
  desired_capacity   = 0
  max_size           = 10
  min_size           = 0
  health_check_grace_period = 300
  # force delete scale in protected instances when running terraform destroy
  force_delete = true
  # default 300
  default_cooldown = 300
  # This option is required if you're planning to use ECS Managed Scaling
  protect_from_scale_in = true

  tag {
    key                 = "ECSCluster"
    value               = local.cluster_name
    propagate_at_launch = true
  }

  mixed_instances_policy {
    instances_distribution {
      on_demand_base_capacity                  = 0
      on_demand_percentage_above_base_capacity = 0
      spot_allocation_strategy                 = "capacity-optimized"
    }
    launch_template {
      launch_template_specification {
        launch_template_id = aws_launch_template.ecs_lt.id
        version = "$Latest"
      }
      override {
        instance_type     = "c5.xlarge"
      }
      override {
        instance_type     = "c4.xlarge"
      }
      override {
        instance_type     = "m5.xlarge"
      }
      override {
        instance_type     = "m4.xlarge"
      }
      override {
        instance_type     = "r5.xlarge"
      }
      override {
        instance_type     = "r4.xlarge"
      }
    }  
  }
  
}

resource "aws_autoscaling_group" "ecs_od_asg" {
  name = "${local.name}-od-asg"

  vpc_zone_identifier = data.aws_subnet_ids.subnets.ids
  desired_capacity   = 0
  max_size           = 10
  min_size           = 0
  health_check_grace_period = 300
  # force delete scale in protected instances when running terraform destroy
  force_delete = true
  # default 300
  default_cooldown = 300
  # This option is required if you're planning to use ECS Managed Scaling
  protect_from_scale_in = true

  tag {
    key                 = "ECSCluster"
    value               = local.cluster_name
    propagate_at_launch = true
  }
  
  mixed_instances_policy {
    instances_distribution {
      on_demand_base_capacity                  = 0
      on_demand_percentage_above_base_capacity = 100
      spot_allocation_strategy                 = "capacity-optimized"
    }
    launch_template {
      launch_template_specification {
        launch_template_id = aws_launch_template.ecs_lt.id
        version = "$Latest"
      }
      override {
        instance_type     = "c5.xlarge"
      }
      override {
        instance_type     = "c4.xlarge"
      }
      override {
        instance_type     = "m5.xlarge"
      }
      override {
        instance_type     = "m4.xlarge"
      }
      override {
        instance_type     = "r5.xlarge"
      }
      override {
        instance_type     = "r4.xlarge"
      }
    }  
  }
  
}
## Create Capacity providers
resource "aws_ecs_capacity_provider" "cp_spot" {
  name = "cp_spot"

  auto_scaling_group_provider {
    auto_scaling_group_arn = aws_autoscaling_group.ecs_spot_asg.arn
    managed_termination_protection = "ENABLED"

    managed_scaling {
      status                    = "ENABLED"
      target_capacity           = 100
    }
  }

}
resource "aws_ecs_capacity_provider" "cp_od" {
  name = "cp_od"

  auto_scaling_group_provider {
    auto_scaling_group_arn = aws_autoscaling_group.ecs_od_asg.arn
    managed_termination_protection = "ENABLED"

    managed_scaling {
      status                    = "ENABLED"
      target_capacity           = 100
    }
  }

}
## Create ECS Cluster
resource "aws_ecs_cluster" "ecs_cluster" {
  name = local.cluster_name

  capacity_providers = ["FARGATE", "FARGATE_SPOT", aws_ecs_capacity_provider.cp_od.name,aws_ecs_capacity_provider.cp_spot.name]

  default_capacity_provider_strategy {
      capacity_provider = aws_ecs_capacity_provider.cp_spot.name
      weight            = "1"
    }
  default_capacity_provider_strategy {
      capacity_provider = aws_ecs_capacity_provider.cp_od.name
      weight            = "1"
    }
  # by default container insights are enabled, adding this setting if customer wants to disable it
  setting {
    name = "containerInsights"
    value = "enabled"
  }
}