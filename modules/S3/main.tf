# modules/S3/main.tf

# Bucket for storing raw meeting audio recordings
resource "aws_s3_bucket" "recordings" {
  bucket = "${var.project_name}-recordings-${var.environment}"

  tags = merge(
    var.tags,
    {
      "Name" = "${var.project_name}-recordings-${var.environment}"
    }
  )
}

# Block all public access for security best practices
resource "aws_s3_bucket_public_access_block" "recordings" {
  bucket = aws_s3_bucket.recordings.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Enable versioning to protect against accidental deletions
resource "aws_s3_bucket_versioning" "recordings" {
  bucket = aws_s3_bucket.recordings.id
  versioning_configuration {
    status = "Enabled"
  }
}

# Enforce server-side encryption for all objects
resource "aws_s3_bucket_server_side_encryption_configuration" "recordings" {
  bucket = aws_s3_bucket.recordings.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Bucket for storing access logs from the main recordings bucket
resource "aws_s3_bucket" "logs" {
  bucket = "${var.project_name}-recordings-logs-${var.environment}"

  tags = merge(
    var.tags,
    {
      "Name" = "${var.project_name}-recordings-logs-${var.environment}"
    }
  )
}

# Block public access for the log bucket
resource "aws_s3_bucket_public_access_block" "logs" {
  bucket = aws_s3_bucket.logs.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Configure server-side access logging on the recordings bucket
resource "aws_s3_bucket_logging" "recordings" {
  bucket = aws_s3_bucket.recordings.id

  target_bucket = aws_s3_bucket.logs.id
  target_prefix = "log/"
}

# This is the key integration piece for our workflow.
# It sends a notification to our SQS queue whenever a new audio file is uploaded.
resource "aws_s3_bucket_notification" "recordings_sqs_notification" {
 bucket = aws_s3_bucket.recordings.id

  queue {
    queue_arn     = var.sqs_queue_arn
    events        = ["s3:ObjectCreated:*"]
    filter_suffix = "" # You can expand this or create multiple blocks for .wav, .m4a etc.
  }

    # This depends on the SQS queue having a policy that allows S3 to send messages to it.
    # We will create that policy in the SQS module.
}
# --- NEW: S3 to SQS Notification ---
# This "linking" resource now lives in the root module for the environment.
# It depends on both the S3 bucket and the SQS queue having been created.
/*
resource "aws_s3_bucket_notification" "recordings_sqs_notification" {
  bucket = module.s3.recordings_bucket_id

  queue {
    queue_arn     = module.sqs.queue_arn
    events        = ["s3:ObjectCreated:*"]
    filter_suffix = ".mp3"
  }

  # This resource implicitly depends on the aws_sqs_queue_policy created in the SQS module.
  # Terraform is smart enough to see this relationship.
}*/