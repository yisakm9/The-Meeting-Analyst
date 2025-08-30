# environments/dev/terraform.tfvars

aws_region   = "us-east-1"
project_name = "meeting-analyst"
environment  = "dev"

tags = {
  Project     = "meeting-analyst"
  Environment = "dev"
  ManagedBy   = "Terraform"
}