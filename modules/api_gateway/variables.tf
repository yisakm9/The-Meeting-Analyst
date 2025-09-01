# modules/api_gateway/variables.tf

variable "project_name" {
  description = "The name of the project."
  type        = string
}

variable "environment" {
  description = "The deployment environment."
  type        = string
}

variable "tags" {
  description = "A map of tags to assign to the resources."
  type        = map(string)
  default     = {}
}

variable "getter_lambda_invoke_arn" {
  description = "The ARN for the Lambda function that API Gateway will invoke."
  type        = string
}