# modules/SQS/main.tf

resource "aws_sqs_queue" "processing_queue" {
  name                       = "${var.project_name}-processing-queue-${var.environment}"
  visibility_timeout_seconds = var.visibility_timeout_seconds

  # For production, consider configuring a dead-letter queue (DLQ)
  # redrive_policy = jsonencode({
  #   deadLetterTargetArn = aws_sqs_queue.processing_dlq.arn
  #   maxReceiveCount     = 4
  # })

  tags = merge(
    var.tags,
    {
      "Name" = "${var.project_name}-processing-queue-${var.environment}"
    }
  )
}

# This data source constructs the IAM policy document in HCL format.
data "aws_iam_policy_document" "sqs_queue_policy" {
  statement {
    effect    = "Allow"
    actions   = ["sqs:SendMessage"]
    resources = [aws_sqs_queue.processing_queue.arn]

    principals {
      type        = "Service"
      identifiers = ["s3.amazonaws.com"]
    }

    # This condition is a security best practice. It ensures that only our
    # specific S3 bucket can send messages to this queue.
    condition {
      test     = "ArnEquals"
      variable = "aws:SourceArn"
      values   = [var.s3_recordings_bucket_arn]
    }
  }
}

# Attaches the policy document to the SQS queue.
resource "aws_sqs_queue_policy" "processing_queue_policy" {
  queue_url = aws_sqs_queue.processing_queue.id
  policy    = data.aws_iam_policy_document.sqs_queue_policy.json
}