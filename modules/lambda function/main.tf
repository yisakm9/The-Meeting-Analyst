# modules/lambda_function/main.tf

# This data source creates a ZIP archive of our Python code from the src directory.
data "archive_file" "lambda_package" {
  type        = "zip"
  source_dir  = var.source_code_path
  output_path = "${path.module}/lambda_package.zip"
}

# Create the AWS Lambda function resource
resource "aws_lambda_function" "summarizer" {
  function_name    = "${var.project_name}-summarizer-${var.environment}"
  role             = var.lambda_execution_role_arn
  handler          = var.handler
  runtime          = var.runtime
  timeout          = var.timeout
  memory_size      = var.memory_size
  
  filename         = data.archive_file.lambda_package.output_path
  source_code_hash = data.archive_file.lambda_package.output_base64sha256
# --- NEW ---
  # Pass the S3 bucket name to the function as an environment variable
  environment {
    variables = {
      OUTPUT_BUCKET_NAME = var.s3_output_bucket_name
    }
  }
  
  tags = merge(
    var.tags,
    {
      "Name" = "${var.project_name}-summarizer-${var.environment}"
    }
  )
}

# Create the Event Source Mapping to link the SQS queue to the Lambda function.
# This grants Lambda permission to poll the queue and tells it to do so.
resource "aws_lambda_event_source_mapping" "sqs_trigger" {
  event_source_arn = var.sqs_processing_queue_arn
  function_name    = aws_lambda_function.summarizer.arn
  enabled          = true
  batch_size       = 1 # Process one meeting at a time for simplicity.
}