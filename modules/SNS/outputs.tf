# modules/SNS/outputs.tf

output "topic_arn" {
  description = "The ARN of the SNS topic for notifications."
  value       = aws_sns_topic.notifications.arn
}