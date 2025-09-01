# modules/lambda_function/outputs.tf

output "lambda_function_arn" {
  description = "The ARN of the created Lambda function."
  value       = aws_lambda_function.summarizer.arn
}

output "lambda_function_name" {
  description = "The name of the created Lambda function."
  value       = aws_lambda_function.summarizer.function_name
}

output "getter_lambda_invoke_arn" {
  description = "The invoke ARN for the getter Lambda function."
  value       = aws_lambda_function.getter.invoke_arn
}