# modules/S3/variables.tf

variable "project_name" {
  description = "The name of the project, used to construct resource names."
  type        = string
}

variable "environment" {
  description = "The deployment environment (e.g., dev, stg, prod)."
  type        = string
}
/*
variable "sqs_queue_arn" {
  description = "The ARN of the SQS queue that will receive notifications from this bucket."
  type        = string
}
*/
variable "tags" {
  description = "A map of tags to assign to the resources."
  type        = map(string)
  default     = {}
}
