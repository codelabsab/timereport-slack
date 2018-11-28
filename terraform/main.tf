# Specify the provider and access details
provider "aws" {
  region = "${var.aws_region}"
  version = "~> 1.41"
}

provider "archive" {
  version = "~> 1.0"
}

# get accountID
data "aws_caller_identity" "accountId" {}

# approval lambda
# archive zip file
data "archive_file" "api" {
  type        = "zip"
  source_file = "${path.module}/../timereport/api.py"
  output_path = "${path.module}/.terraform/archive_files/api.zip"
}

# remote store on s3
terraform {
  backend "s3" {
    bucket = "terraform.codelabs.se"
    key    = "slack/timereport/"
    region = "us-east-1"
  }
}
