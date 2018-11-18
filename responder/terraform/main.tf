# Specify the provider and access details
provider "aws" {
  region  = "${var.aws_region}"
  version = "~> 1.45"
}

provider "archive" {
  version = "~> 1.1"
}

# get accountID
data "aws_caller_identity" "accountId" {}

data "aws_ssm_parameter" "slack_responder_webhook_url" {
  name = "/slack/responder/webhook_url"
}

# responder main lambda
# archive zip file
data "archive_file" "__main__" {
  type        = "zip"
  source_dir = "${path.module}/../responder/"
  output_path = "${path.module}/.terraform/archive_files/__main__.zip"
}

# remote store on s3
terraform {
  backend "s3" {
    bucket = "terraform.codelabs.se"
    key    = "slack/responder/"
    region = "us-east-1"
  }
}
