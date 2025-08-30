# modules/S3/outputs.tf

output "recordings_bucket_id" {
  description = "The ID (name) of the S3 bucket for audio recordings."
  value       = aws_s3_bucket.recordings.id
}

output "recordings_bucket_arn" {
  description = "The ARN of the S3 bucket for audio recordings."
  value       = aws_s3_bucket.recordings.arn
}