# modules/api_gateway/outputs.tf
output "api_endpoint" {
  description = "The invocation URL for the API."
  value       = aws_apigatewayv2_api.main.api_endpoint
}
output "api_execution_arn" {
  description = "The execution ARN of the API, used for Lambda permissions."
  value       = aws_apigatewayv2_api.main.execution_arn
}