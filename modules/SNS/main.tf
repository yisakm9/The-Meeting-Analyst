# modules/SNS/main.tf

resource "aws_sns_topic" "notifications" {
  name = "${var.project_name}-notifications-${var.environment}"

  tags = merge(
    var.tags,
    {
      "Name" = "${var.project_name}-notifications-${var.environment}"
    }
  )
}

# Creates an email subscription if an email address is provided.
# IMPORTANT: AWS will send a confirmation email to this address.
# You must click the link in that email to activate the subscription.
resource "aws_sns_topic_subscription" "email_subscription" {
  # Only create this resource if the email variable is not an empty string
  count = var.subscription_email_address != "" ? 1 : 0

  topic_arn = aws_sns_topic.notifications.arn
  protocol  = "email"
  endpoint  = var.subscription_email_address
}