# environments/dev/variables.tf

variable "aws_region" {
  description = "The AWS region to deploy resources into."
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "The unique name for the project."
  type        = string
  default     = "transcribe"
}

variable "environment" {
  description = "The name of the deployment environment."
  type        = string
  default     = "dev"
}

variable "tags" {
  description = "A map of common tags to apply to all resources."
  type        = map(string)
  default     = "dev"

}

