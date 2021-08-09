terraform {
  required_version = ">= 0.12.26"

  required_providers {
    aws      = ">= 3.32"
    template = ">= 2.2"
  }
}
provider "aws" {
  region = "us-east-1"
}
