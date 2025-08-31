# environments/dev/main.tf

# Configure the AWS Provider for the 'dev' environment
provider "aws" {
  region = var.aws_region
}
# --- IAM Role and Policy for Lambda ---
#
# Call the IAM module. It depends on the outputs from both the S3 and SQS
# modules to build its least-privilege policy.
module "iam" {
  source = "../../modules/iam"

  project_name             = var.project_name
  environment              = var.environment
  tags                     = var.tags
  s3_recordings_bucket_arn = module.s3.recordings_bucket_arn
  sqs_processing_queue_arn = module.sqs.queue_arn
}


# --- S3 Buckets for Recordings and Logs ---
#
# Call the S3 module. We now replace the placeholder with the actual
# ARN from the output of our new "sqs" module.

module "s3" {
  source = "../../modules/S3"

  project_name  = var.project_name
  environment   = var.environment
  tags          = var.tags
# sqs_queue_arn = module.sqs.queue_arn # <-- UPDATED from placeholder
}

# --- SQS Queue for Processing Jobs ---
#
# Call the SQS module. We must provide the ARN of the S3 bucket,
# which we get from the output of the "s3" module below.
# This creates a dependency between the resources.

module "sqs" {
  source = "../../modules/SQS"

  project_name             = var.project_name
  environment              = var.environment
  tags                     = var.tags
  s3_recordings_bucket_arn = module.s3.recordings_bucket_arn
}


# --- Lambda Function ---
#
# Call the Lambda function module, providing the necessary ARNs
# from the IAM and SQS modules.

module "lambda_function" {
  source = "../../modules/lambda function"

  project_name              = var.project_name
  environment               = var.environment
  tags                      = var.tags
  lambda_execution_role_arn = module.iam.lambda_execution_role_arn
  sqs_processing_queue_arn  = module.sqs.queue_arn
  source_code_path          = "../../src/lambda summarizer"
  s3_output_bucket_name     = module.s3.recordings_bucket_id
}


