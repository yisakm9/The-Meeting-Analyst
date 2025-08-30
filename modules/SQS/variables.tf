# modules/SQS/variables.tf

variable "project_name" {
  description = "The name of the project, used to construct resource names."
  type        = string
}

variable "environment" {
  description = "The deployment environment (e.g., dev, stg, prod)."
  type        = string
}

variable "s3_recordings_bucket_arn" {
  description = "The ARN of the S3 bucket that is allowed to send notifications to this queue."
  type        = string
}

variable "tags" {
  description = "A map of tags to assign to the resources."
  type        = map(string)
  default     = {}
}

variable "visibility_timeout_seconds" {
  description = "The visibility timeout for the queue. Should be longer than the expected Lambda function execution time."
  type        = number
  default     = 300 # 5 minutes
}