# modules/api_gateway/main.tf

# 1. Create the main HTTP API resource
resource "aws_apigatewayv2_api" "main" {
  name          = "${var.project_name}-api-${var.environment}"
  protocol_type = "HTTP"
  tags          = var.tags
}

# 2. Create a default stage that auto-deploys changes
resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.main.id
  name        = "$default"
  auto_deploy = true
  tags        = var.tags
}

# 3. Create the integration between the API and our getter Lambda
resource "aws_apigatewayv2_integration" "getter_lambda" {
  api_id           = aws_apigatewayv2_api.main.id
  integration_type = "AWS_PROXY"
  integration_uri  = var.getter_lambda_invoke_arn
}

# 4. Define the public route: GET /meetings/{meetingId}
resource "aws_apigatewayv2_route" "get_meeting" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "GET /meetings/{meetingId}"
  target    = "integrations/${aws_apigatewayv2_integration.getter_lambda.id}"
}