# general iam role for lambda
resource "aws_iam_role" "iam_for_lambda" {
  name = "iam_for_lambda"
  lifecycle {
    ignore_changes = [
      "assume_role_policy",
    ]
  }

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com",
        "Service": "apigateway.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}
