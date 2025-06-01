# Archive source code for Lambda deployment
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "../src"
  output_path = "../dist/lambda_function.zip"
}

# Entry Lambda function
resource "aws_lambda_function" "entry_lambda" {
  filename         = data.archive_file.lambda_zip.output_path
  function_name    = "${var.project_name}-entry"
  role             = aws_iam_role.lambda_role.arn
  handler          = "handlers.entry.lambda_handler"
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  runtime          = "python3.12"
  timeout          = 30

  environment {
    variables = {
      PARKING_TABLE_NAME        = aws_dynamodb_table.parking_tickets.name
      HOURLY_RATE               = var.hourly_rate
      BILLING_INCREMENT_MINUTES = var.billing_increment_minutes
    }
  }

  tags = {
    Name        = "ParkingEntryFunction"
    Environment = var.environment
    Project     = "parking-lot-system"
  }
}

# Exit Lambda function
resource "aws_lambda_function" "exit_lambda" {
  filename         = data.archive_file.lambda_zip.output_path
  function_name    = "${var.project_name}-exit"
  role             = aws_iam_role.lambda_role.arn
  handler          = "handlers.exit.lambda_handler"
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  runtime          = "python3.12"
  timeout          = 30

  environment {
    variables = {
      PARKING_TABLE_NAME        = aws_dynamodb_table.parking_tickets.name
      HOURLY_RATE               = var.hourly_rate
      BILLING_INCREMENT_MINUTES = var.billing_increment_minutes
    }
  }

  tags = {
    Name        = "ParkingExitFunction"
    Environment = var.environment
    Project     = "parking-lot-system"
  }
}

# CloudWatch Log Groups for Lambda functions
resource "aws_cloudwatch_log_group" "entry_lambda_logs" {
  name              = "/aws/lambda/${aws_lambda_function.entry_lambda.function_name}"
  retention_in_days = var.log_retention_days

  tags = {
    Name        = "ParkingEntryLogs"
    Environment = var.environment
    Project     = "parking-lot-system"
  }
}

resource "aws_cloudwatch_log_group" "exit_lambda_logs" {
  name              = "/aws/lambda/${aws_lambda_function.exit_lambda.function_name}"
  retention_in_days = var.log_retention_days

  tags = {
    Name        = "ParkingExitLogs"
    Environment = var.environment
    Project     = "parking-lot-system"
  }
} 