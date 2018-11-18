# account
resource "aws_api_gateway_account" "slack-responder-account" {
  cloudwatch_role_arn = "${aws_iam_role.iam_for_lambda.arn}"
}

# api gateway for message_actions
resource "aws_api_gateway_rest_api" "slack-responder-api" {
  name        = "slack-responder"
  description = "Slack sns message action response url for yes or no button"
}
# create resource for api gateway
resource "aws_api_gateway_resource" "slack-responder-resource" {
  rest_api_id = "${aws_api_gateway_rest_api.slack-responder-api.id}"
  parent_id   = "${aws_api_gateway_rest_api.slack-responder-api.root_resource_id}"
  path_part   = "message_action"
}
# create method for api gateway
resource "aws_api_gateway_method" "slack-responder-method" {
  rest_api_id   = "${aws_api_gateway_rest_api.slack-responder-api.id}"
  resource_id   = "${aws_api_gateway_resource.slack-responder-resource.id}"
  http_method   = "POST"
  authorization = "NONE"
}
# create method settings for api gateway
resource "aws_api_gateway_method_settings" "slack-responder-method-settings" {
  rest_api_id = "${aws_api_gateway_rest_api.slack-responder-api.id}"
  stage_name  = "${aws_api_gateway_deployment.slack-responder-deployment.stage_name}"
  method_path = "${aws_api_gateway_resource.slack-responder-resource.path_part}/${aws_api_gateway_method.slack-responder-method.http_method}"

  settings {
    metrics_enabled = true
    logging_level = "INFO"
  }
}
# gateway method response 200
resource "aws_api_gateway_method_response" "method-response-200" {
  rest_api_id         = "${aws_api_gateway_rest_api.slack-responder-api.id}"
  resource_id         = "${aws_api_gateway_resource.slack-responder-resource.id}"
  http_method         = "${aws_api_gateway_method.slack-responder-method.http_method}"
  status_code         = "200"
  depends_on          = ["aws_api_gateway_integration.slack-responder-integration"]
  response_models     { "application/json" = "Empty" }
}

# create integration for api gateway
resource "aws_api_gateway_integration" "slack-responder-integration" {
  rest_api_id = "${aws_api_gateway_rest_api.slack-responder-api.id}"
  resource_id = "${aws_api_gateway_resource.slack-responder-resource.id}"
  http_method = "${aws_api_gateway_method.slack-responder-method.http_method}"
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = "arn:aws:apigateway:${var.aws_region}:lambda:path/2015-03-31/functions/${aws_lambda_function.responder-main.arn}/invocations"
  passthrough_behavior    = "WHEN_NO_MATCH"
  content_handling        = "CONVERT_TO_TEXT"
}

# create deployment for api gateway
resource "aws_api_gateway_deployment" "slack-responder-deployment" {
  depends_on = ["aws_api_gateway_integration.slack-responder-integration"]
  rest_api_id = "${aws_api_gateway_rest_api.slack-responder-api.id}"
  stage_name = "prod"
}

# output for the gateway
output "Add this as your Request URL to SLACK interactive components section" {
  value = "https://${aws_api_gateway_deployment.slack-responder-deployment.rest_api_id}.execute-api.${var.aws_region}.amazonaws.com/${aws_api_gateway_deployment.slack-responder-deployment.stage_name}/${aws_api_gateway_resource.slack-responder-resource.path_part}"
}
