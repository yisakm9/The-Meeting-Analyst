# environments/dev/outputs.tf

output "s3_recordings_bucket_id" {
  description = "The ID of the S3 bucket for audio recordings."
  value       = module.s3.recordings_bucket_id
}

output "s3_recordings_bucket_arn" {
  description = "The ARN of the S3 bucket for audio recordings."
  value       = module.s3.recordings_bucket_arn
}
# --- SQS Outputs (newly added) ---
output "sqs_processing_queue_arn" {
  description = "The ARN of the SQS queue for processing meeting recordings."
  value       = module.sqs.queue_arn
}

output "sqs_processing_queue_url" {
  description = "The URL of the SQS queue for processing meeting recordings."
  value       = module.sqs.queue_url
}

# --- Lambda Outputs ---
output "lambda_summarizer_function_arn" {
  description = "The ARN of the summarizer Lambda function."
  value       = module.lambda_function.lambda_function_arn
}