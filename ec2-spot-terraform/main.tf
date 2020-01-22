variable "region" {
  default = "us-east-1"
}

variable "shared_credentials_file" {
  default = "/home/ec2-user/.aws/credentials"
}

variable "profile" {
  default = "terraform"
}

provider "aws" {
  region                  = "${var.region}"
  shared_credentials_file = "${var.shared_credentials_file}"
  profile                 = "${var.profile}"
}


resource "aws_instance" "web" {
  ami           = "ami-062f7200baf2fa504"
  instance_type = "t2.micro"

  tags = {
    Name = "HelloWorld"
  }
}

resource "aws_launch_template" "spot-demo-lt" {
  name = "spot-demo-lt"


  image_id = "ami-062f7200baf2fa504"


  instance_type = "t3.micro"

  key_name = "awsajp_keypair"


  monitoring {
    enabled = true
  }

  placement {
    availability_zone = "us-east-1a,us-east-1b,us-east-1c,us-east-1d,us-east-1e,us-east-1f"
  }


  tag_specifications {
    resource_type = "instance"

    tags = {
      Name = "test"
    }
  }

}


resource "aws_autoscaling_group" "spot-demo-asg" {
  availability_zones = ["us-east-1a", "us-east-1b", "us-east-1c", "us-east-1d", "us-east-1e", "us-east-1f"]
  desired_capacity   = 3
  max_size           = 6
  min_size           = 3

  mixed_instances_policy {
    launch_template {
      launch_template_specification {
        launch_template_id = "${aws_launch_template.spot-demo-lt.id}"
        version = "$Default"
      }

      override {
        instance_type = "m4.large"
        weighted_capacity = "1"
      }

      override {
        instance_type = "c4.large"
        weighted_capacity = "2"
      }
    }
    
    instances_distribution {
      on_demand_allocation_strategy = "prioritized"
      on_demand_base_capacity = 1
      on_demand_percentage_above_base_capacity = 50
      spot_allocation_strategy = "lowest-price"
      spot_instance_pools = 2
    }
    
    }

}

