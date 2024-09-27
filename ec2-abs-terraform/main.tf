terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.16.0"
    }
  }
}

data "aws_ami" "x86" {
  most_recent = true

  owners = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-kernel-5.10-hvm-*-x86_64-gp2"]
  }

  filter {
    name   = "owner-alias"
    values = ["amazon"]
  }
}

data "aws_ami" "arm" {
  most_recent = true

  owners = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-kernel-5.10-hvm-*-arm64-gp2"]
  }

  filter {
    name   = "owner-alias"
    values = ["amazon"]
  }
}


resource "aws_launch_template" "x86" {
  name_prefix   = "x86"
  image_id      = data.aws_ami.x86.id
  instance_type = "c5.large"
}

resource "aws_launch_template" "arm" {
  name_prefix   = "arm"
  image_id      = data.aws_ami.arm.id
  instance_type = "c6g.large"
}

resource "aws_launch_template" "abs" {
  name_prefix = "abs"
  image_id    = data.aws_ami.x86.id

  instance_requirements {
    memory_mib {
      min = 8192
    }

    vcpu_count {
      min = 4
    }

    instance_generations = ["current"]
  }
}

resource "aws_autoscaling_group" "on_demand" {
  availability_zones = ["us-east-1a", "us-east-1b", "us-east-1c"]
  max_size           = 1
  min_size           = 1

  mixed_instances_policy {
    launch_template {
      launch_template_specification {
        launch_template_id = aws_launch_template.abs.id
      }
    }
  }
}

resource "aws_autoscaling_group" "spot" {
  availability_zones = ["us-east-1a", "us-east-1b", "us-east-1c"]
  desired_capacity   = 1
  max_size           = 1
  min_size           = 1
  capacity_rebalance = true

  mixed_instances_policy {
    instances_distribution {
      spot_allocation_strategy = "capacity-optimized"
    }

    launch_template {
      launch_template_specification {
        launch_template_id = aws_launch_template.x86.id
      }

      override {
        instance_requirements {
          memory_mib {
            min = 4096
            max = 32768
          }

          vcpu_count {
            min = 2
          }

          memory_gib_per_vcpu {
            min = 4
            max = 4
          }

          accelerator_count {
            max = 0
          }
        }
      }
    }
  }
}

resource "aws_ec2_fleet" "spot" {
  target_capacity_specification {
    default_target_capacity_type = "spot"
    total_target_capacity        = 5
  }

  spot_options {
    allocation_strategy = "capacity-optimized"
    maintenance_strategies {
      capacity_rebalance {
        replacement_strategy = "launch"
      }
    }
  }

  launch_template_config {
    launch_template_specification {
      launch_template_id = aws_launch_template.x86.id
      version            = aws_launch_template.x86.latest_version
    }

    override {
      instance_requirements {
        memory_mib {
          min = 65536
          max = 73728
        }

        vcpu_count {
          min = 32
          max = 36
        }

        cpu_manufacturers   = ["intel"]
        local_storage       = "required"
        local_storage_types = ["ssd"]

        total_local_storage_gb {
          min = 100
        }
      }
    }
  }
}

resource "aws_autoscaling_group" "on_demand_spot" {
  availability_zones = ["us-east-1a", "us-east-1b", "us-east-1c"]
  desired_capacity   = 4
  max_size           = 10
  min_size           = 2
  capacity_rebalance = true

  mixed_instances_policy {
    instances_distribution {
      on_demand_base_capacity                  = 2
      on_demand_percentage_above_base_capacity = 0
      spot_allocation_strategy                 = "capacity-optimized"
    }

    launch_template {
      launch_template_specification {
        launch_template_id = aws_launch_template.arm.id
      }

      override {
        launch_template_specification {
          launch_template_id = aws_launch_template.arm.id
        }

        instance_requirements {
          memory_mib {
            min = 16384
            max = 16384
          }

          vcpu_count {
            max = 4
          }
        }
      }

      override {
        launch_template_specification {
          launch_template_id = aws_launch_template.abs.id
        }

        instance_requirements {
          memory_mib {
            min = 16384
          }

          vcpu_count {
            min = 4
          }
        }
      }
    }
  }
}
