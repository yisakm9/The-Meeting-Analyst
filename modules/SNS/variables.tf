# modules/SNS/variables.tf

variable "project_name" {
  description = "The name of the project."
  type        = string
}

variable "environment" {
  description = "The deployment environment."
  type        = string
}

variable "subscription_email_address" {
  description = "The email address to subscribe to the SNS topic for notifications. Optional."
  type        = string
  default     = ""
}

variable "tags" {
  description = "A map of tags to assign to the resources."
  type        = map(string)
  default     = {}
}