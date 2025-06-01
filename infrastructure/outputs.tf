output "api_gateway_url" {
  description = "API Gateway endpoint URL"
  value       = "https://${aws_api_gateway_rest_api.parking_api.id}.execute-api.${var.aws_region}.amazonaws.com/v1"
}

output "dynamodb_table_name" {
  description = "DynamoDB table name"
  value       = aws_dynamodb_table.parking_tickets.name
}

output "dynamodb_table_arn" {
  description = "DynamoDB table ARN"
  value       = aws_dynamodb_table.parking_tickets.arn
}

output "entry_lambda_arn" {
  description = "Entry Lambda function ARN"
  value       = aws_lambda_function.entry_lambda.arn
}

output "exit_lambda_arn" {
  description = "Exit Lambda function ARN"
  value       = aws_lambda_function.exit_lambda.arn
}

output "api_gateway_rest_api_id" {
  description = "API Gateway REST API ID"
  value       = aws_api_gateway_rest_api.parking_api.id
}

output "lambda_role_arn" {
  description = "Lambda execution role ARN"
  value       = aws_iam_role.lambda_role.arn
} 