# account
resource "aws_api_gateway_account" "account" {
  cloudwatch_role_arn = "${aws_iam_role.iam_for_lambda.arn}"
}

# api gateway for message_actions
resource "aws_api_gateway_rest_api" "api" {
  name        = "timereport"
  description = "timereport"
}
# create resource for api gateway
resource "aws_api_gateway_resource" "resource" {
  rest_api_id = "${aws_api_gateway_rest_api.api.id}"
  parent_id   = "${aws_api_gateway_rest_api.api.root_resource_id}"
  path_part   = "timereport"
}
# create method for api gateway
resource "aws_api_gateway_method" "method" {
  rest_api_id   = "${aws_api_gateway_rest_api.api.id}"
  resource_id   = "${aws_api_gateway_resource.resource.id}"
  http_method   = "POST"
  authorization = "NONE"
}
# create method settings for api gateway
resource "aws_api_gateway_method_settings" "method-settings" {
  rest_api_id = "${aws_api_gateway_rest_api.api.id}"
  stage_name  = "${aws_api_gateway_deployment.deployment.stage_name}"
  method_path = "${aws_api_gateway_resource.resource.path_part}/${aws_api_gateway_method.method.http_method}"

  settings {
    metrics_enabled = false
    logging_level = "off"
  }
}
# gateway method response 200
resource "aws_api_gateway_method_response" "method-response-200" {
  rest_api_id         = "${aws_api_gateway_rest_api.api.id}"
  resource_id         = "${aws_api_gateway_resource.resource.id}"
  http_method         = "${aws_api_gateway_method.method.http_method}"
  status_code         = "200"
  depends_on          = ["aws_api_gateway_integration.integration"]
  response_models     { "application/json" = "Empty" }
}

# create integration for api gateway
resource "aws_api_gateway_integration" "integration" {
  rest_api_id = "${aws_api_gateway_rest_api.api.id}"
  resource_id = "${aws_api_gateway_resource.resource.id}"
  http_method = "${aws_api_gateway_method.method.http_method}"
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = "arn:aws:apigateway:${var.aws_region}:lambda:path/2015-03-31/functions/${aws_lambda_function.api.arn}/invocations"
  passthrough_behavior    = "WHEN_NO_MATCH"
  content_handling        = "CONVERT_TO_TEXT"
}

# create deployment for api gateway
resource "aws_api_gateway_deployment" "deployment" {
  depends_on = ["aws_api_gateway_integration.integration"]
  rest_api_id = "${aws_api_gateway_rest_api.api.id}"
  stage_name = "prod"
}

# output for the gateway
output "Add this as your Request URL to SLACK interactive components section" {
  value = "https://${aws_api_gateway_deployment.deployment.rest_api_id}.execute-api.${var.aws_region}.amazonaws.com/${aws_api_gateway_deployment.deployment.stage_name}/${aws_api_gateway_resource.resource.path_part}"
}
