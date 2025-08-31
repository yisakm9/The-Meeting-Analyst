# modules/DynamoDB/main.tf

resource "aws_dynamodb_table" "meeting_transcripts" {
  name         = "${var.project_name}-transcripts-${var.environment}"
  billing_mode = "PAY_PER_REQUEST" # Cost-effective for unpredictable workloads
  hash_key     = "MeetingID"

  attribute {
    name = "MeetingID"
    type = "S" # S for String
  }

  tags = merge(
    var.tags,
    {
      "Name" = "${var.project_name}-transcripts-${var.environment}"
    }
  )
}