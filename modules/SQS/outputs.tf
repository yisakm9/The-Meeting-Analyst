# modules/SQS/outputs.tf

output "queue_arn" {
  description = "The ARN of the SQS queue."
  value       = aws_sqs_queue.processing_queue.arn
}

output "queue_url" {
  description = "The URL of the SQS queue."
  value       = aws_sqs_queue.processing_queue.id
}

output "queue_name" {
  description = "The name of the SQS queue."
  value       = aws_sqs_queue.processing_queue.name
}