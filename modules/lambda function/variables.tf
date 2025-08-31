# modules/lambda_function/variables.tf

variable "project_name" {
  description = "The name of the project."
  type        = string
}

variable "environment" {
  description = "The deployment environment."
  type        = string
}

variable "lambda_execution_role_arn" {
  description = "The ARN of the IAM role for the Lambda function."
  type        = string
}

variable "sqs_processing_queue_arn" {
  description = "The ARN of the SQS queue that will trigger this Lambda."
  type        = string
}

variable "source_code_path" {
  description = "The local path to the Lambda function's source code directory."
  type        = string
}

variable "handler" {
  description = "The function entrypoint in your code."
  type        = string
  default     = "index.handler"
}

variable "runtime" {
  description = "The runtime environment for the Lambda function."
  type        = string
  default     = "python3.9"
}

variable "timeout" {
  description = "The amount of time in seconds that the Lambda has to run."
  type        = number
  # This should be >= the SQS visibility timeout to avoid reprocessing.
  default     = 300
}

variable "memory_size" {
  description = "The amount of memory in MB to allocate to the function."
  type        = number
  default     = 256
}

variable "tags" {
  description = "A map of tags to assign to the resources."
  type        = map(string)
  default     = {}
}

variable "s3_output_bucket_name" {
  description = "The name of the S3 bucket where Transcribe will save its output."
  type        = string
}

#  ( new variables)

variable "processor_source_code_path" {
  description = "The local path to the processor Lambda's source code."
  type        = string
}

variable "processor_handler" {
  description = "The function entrypoint for the processor Lambda."
  type        = string
  default     = "index.handler"
}

variable "transcribe_data_access_role_arn" { # <-- RENAMED
  description = "The ARN of the IAM role that Transcribe will assume for data access."
  type        = string
}