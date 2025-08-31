# modules/iam/outputs.tf

output "lambda_execution_role_arn" {
  description = "The ARN of the IAM role for the Lambda function."
  value       = aws_iam_role.lambda_execution_role.arn
}

output "transcribe_data_access_role_arn" { # <-- RENAMED for clarity
  description = "The ARN of the IAM role for the Transcribe service to assume."
  value       = aws_iam_role.transcribe_service_role.arn
}