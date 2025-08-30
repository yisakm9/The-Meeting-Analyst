# modules/iam/variables.tf

variable "project_name" {
  description = "The name of the project, used to construct resource names."
  type        = string
}

variable "environment" {
  description = "The deployment environment (e.g., dev, stg, prod)."
  type        = string
}

variable "s3_recordings_bucket_arn" {
  description = "The ARN of the S3 bucket from which the Lambda needs to read objects."
  type        = string
}

variable "sqs_processing_queue_arn" {
  description = "The ARN of the SQS queue from which the Lambda needs to read messages."
  type        = string
}

variable "tags" {
  description = "A map of tags to assign to the resources."
  type        = map(string)
  default     = {}
}