# modules/lambda_function/main.tf

# This data source creates a ZIP archive of our Python code from the src directory.
data "archive_file" "summarizer_package" {
  type        = "zip"
  source_dir  = var.source_code_path
  output_path = "${path.module}/summarizer_package.zip"
}

# Create the AWS Lambda function resource
resource "aws_lambda_function" "summarizer" {
  function_name    = "${var.project_name}-summarizer-${var.environment}"
  role             = var.lambda_execution_role_arn
  handler          = var.handler
  runtime          = var.runtime
  timeout          = var.timeout
  memory_size      = var.memory_size
  
  filename         = data.archive_file.summarizer_package.output_path
  source_code_hash = data.archive_file.summarizer_package.output_base64sha256
# --- NEW ---
  # Pass the S3 bucket name to the function as an environment variable
  environment {
    variables = {
      OUTPUT_BUCKET_NAME = var.s3_output_bucket_name
      TRANSCRIBE_DATA_ACCESS_ROLE_ARN = var.transcribe_data_access_role_arn # <-- RENAMED
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

# --- NEW: Function 2: Processor (Result Handler) ---
data "archive_file" "processor_package" {
  type        = "zip"
  source_dir  = var.processor_source_code_path
  output_path = "${path.module}/processor_package.zip"
}

resource "aws_lambda_function" "processor" {
  function_name    = "${var.project_name}-processor-${var.environment}"
  role             = var.lambda_execution_role_arn # Re-using the same role for simplicity
  handler          = var.processor_handler
  runtime          = var.runtime
  timeout          = var.timeout
  memory_size      = var.memory_size
  
  filename         = data.archive_file.processor_package.output_path
  source_code_hash = data.archive_file.processor_package.output_base64sha256

  # We will add environment variables here later for DynamoDB and SNS
  # environment {
  #   variables = { ... }
  # }
  environment {
    variables = {
      DYNAMODB_TABLE_NAME = var.dynamodb_table_name
    }
  }
  
  tags = merge(
    var.tags,
    {
      "Name" = "${var.project_name}-processor-${var.environment}"
    }
  )
}

# --- NEW: EventBridge Rule to Trigger the Processor Lambda ---

# This rule listens for events from AWS Transcribe.
resource "aws_cloudwatch_event_rule" "transcribe_job_state_change" {
  name        = "${var.project_name}-transcribe-job-rule-${var.environment}"
  description = "Triggers the processor Lambda when a Transcribe job completes or fails."

  # The event pattern specifies exactly which events to listen for.
  event_pattern = jsonencode({
    "source" : ["aws.transcribe"],
    "detail-type" : ["Transcribe Job State Change"],
    "detail" : {
      "TranscriptionJobStatus" : ["COMPLETED", "FAILED"]
    }
  })
}

# This target connects the rule to our processor Lambda function.
resource "aws_cloudwatch_event_target" "lambda_processor_target" {
  rule      = aws_cloudwatch_event_rule.transcribe_job_state_change.name
  target_id = "TriggerLambdaProcessor"
  arn       = aws_lambda_function.processor.arn
}

# This grants EventBridge the necessary permission to invoke our Lambda function.
resource "aws_lambda_permission" "allow_eventbridge_to_invoke_processor" {
  statement_id  = "AllowEventBridgeInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.processor.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.transcribe_job_state_change.arn
}