# approval lambda
resource "aws_lambda_function" "api" {
  filename         = "${data.archive_file.api.output_path}"
  function_name    = "api"
  role             = "${aws_iam_role.iam_for_lambda.arn}"
  handler          = "api.lambda_handler"
  source_code_hash = "${data.archive_file.api.output_base64sha256}"
  runtime          = "python3.6"

//  Use our common tags and add a specific name.
  tags = "${merge(
    local.common_tags
  )}"
}

resource "aws_lambda_permission" "allow-api-gateway" {
  statement_id  = "AllowExecutionFromApiGateway"
  action        = "lambda:InvokeFunction"
  function_name = "${aws_lambda_function.api.function_name}"
  principal     = "apigateway.amazonaws.com"
  source_arn    = "arn:aws:execute-api:${var.aws_region}:${data.aws_caller_identity.accountId.account_id}:${aws_api_gateway_rest_api.api.id}/*/${aws_api_gateway_method.method.http_method}${aws_api_gateway_resource.resource.path}"
}
