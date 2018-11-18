# approval lambda
resource "aws_lambda_function" "responder-main" {
  filename         = "${data.archive_file.__main__.output_path}"
  function_name    = "responder-main"
  role             = "${aws_iam_role.iam_for_lambda.arn}"
  handler          = "__main__.lambda_handler"
  source_code_hash = "${data.archive_file.__main__.output_base64sha256}"
  runtime          = "python3.6"

  environment {
    variables = {
      SLACK_WEBHOOK_URL = "${data.aws_ssm_parameter.slack_responder_webhook_url.value}"
    }
  }

//  Use our common tags and add a specific name.
  tags = "${merge(
    local.common_tags
  )}"
}
