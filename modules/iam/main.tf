# modules/iam/main.tf

# This data source defines the "Trust Policy" for our IAM role.
# It specifies that only the AWS Lambda service is allowed to assume this role.
data "aws_iam_policy_document" "lambda_assume_role_policy" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com",
                     "transcribe.amazonaws.com" # <-- NEW
      ]
    }
  }
}

# Create the IAM Role for the Lambda function
resource "aws_iam_role" "lambda_execution_role" {
  name               = "${var.project_name}-lambda-exec-role-${var.environment}"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role_policy.json

  tags = var.tags
}

# This data source constructs the "Permissions Policy" for our role.
# It grants the necessary permissions for S3, SQS, and CloudWatch Logs.
data "aws_iam_policy_document" "lambda_permissions_policy" {
  # Standard permissions for Lambda to write logs to CloudWatch
  statement {
    effect = "Allow"
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
    resources = ["arn:aws:logs:*:*:*"] # Standard practice for basic logging
  }

  # Permissions to read and delete messages from our specific SQS queue
  statement {
    effect = "Allow"
    actions = [
      "sqs:ReceiveMessage",
      "sqs:DeleteMessage",
      "sqs:GetQueueAttributes"
    ]
    resources = [var.sqs_processing_queue_arn]
  }

  # Permission to read objects from our specific S3 bucket.
  # The "/*" is important as permissions apply to objects *within* the bucket.
  statement {
    effect = "Allow"
    actions = [
      "s3:GetObject", # For reading the source audio
      "s3:PutObject"  # For Transcribe to write the output transcript
    ]
    resources = ["${var.s3_recordings_bucket_arn}/*"]
  }

  # --- NEW ---
  # Permission to start an Amazon Transcribe job.
  # The resource is "*" because the ARN for a transcription job is not known
  # until after it has been created.
  statement {
    effect    = "Allow"
    actions   = ["transcribe:StartTranscriptionJob"]
    resources = ["*"]
  }
}

# Create the IAM Policy resource from the policy document
resource "aws_iam_policy" "lambda_permissions_policy" {
  name   = "${var.project_name}-lambda-permissions-policy-${var.environment}"
  policy = data.aws_iam_policy_document.lambda_permissions_policy.json
  tags   = var.tags
}

# Attach the permissions policy to the Lambda execution role
resource "aws_iam_role_policy_attachment" "attach_lambda_permissions" {
  role       = aws_iam_role.lambda_execution_role.name
  policy_arn = aws_iam_policy.lambda_permissions_policy.arn
}

