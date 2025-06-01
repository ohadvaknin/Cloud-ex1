terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# DynamoDB table for parking tickets
resource "aws_dynamodb_table" "parking_tickets" {
  name           = var.table_name
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "ticket_id"

  attribute {
    name = "ticket_id"
    type = "S"
  }

  tags = {
    Name        = "ParkingTickets"
    Environment = var.environment
    Project     = "parking-lot-system"
  }
}

# IAM role for Lambda functions
resource "aws_iam_role" "lambda_role" {
  name = "${var.project_name}-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name        = "ParkingLambdaRole"
    Environment = var.environment
    Project     = "parking-lot-system"
  }
}

# IAM policy for Lambda to access DynamoDB
resource "aws_iam_role_policy" "lambda_dynamodb_policy" {
  name = "${var.project_name}-lambda-dynamodb-policy"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:DeleteItem",
          "dynamodb:Query",
          "dynamodb:Scan"
        ]
        Resource = aws_dynamodb_table.parking_tickets.arn
      }
    ]
  })
}

# Attach basic Lambda execution policy
resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# API Gateway REST API
resource "aws_api_gateway_rest_api" "parking_api" {
  name        = "${var.project_name}-api"
  description = "Parking Lot Management System API"

  endpoint_configuration {
    types = ["REGIONAL"]
  }

  tags = {
    Name        = "ParkingAPI"
    Environment = var.environment
    Project     = "parking-lot-system"
  }
}

# API Gateway deployment
resource "aws_api_gateway_deployment" "parking_api_deployment" {
  depends_on = [
    aws_api_gateway_integration.entry_integration,
    aws_api_gateway_integration.exit_integration,
  ]

  rest_api_id = aws_api_gateway_rest_api.parking_api.id
  stage_name  = var.environment

  lifecycle {
    create_before_destroy = true
  }
}

# /entry resource
resource "aws_api_gateway_resource" "entry_resource" {
  rest_api_id = aws_api_gateway_rest_api.parking_api.id
  parent_id   = aws_api_gateway_rest_api.parking_api.root_resource_id
  path_part   = "entry"
}

# /exit resource
resource "aws_api_gateway_resource" "exit_resource" {
  rest_api_id = aws_api_gateway_rest_api.parking_api.id
  parent_id   = aws_api_gateway_rest_api.parking_api.root_resource_id
  path_part   = "exit"
}

# POST method for /entry
resource "aws_api_gateway_method" "entry_post" {
  rest_api_id   = aws_api_gateway_rest_api.parking_api.id
  resource_id   = aws_api_gateway_resource.entry_resource.id
  http_method   = "POST"
  authorization = "NONE"
}

# POST method for /exit
resource "aws_api_gateway_method" "exit_post" {
  rest_api_id   = aws_api_gateway_rest_api.parking_api.id
  resource_id   = aws_api_gateway_resource.exit_resource.id
  http_method   = "POST"
  authorization = "NONE"
}

# Integration for /entry
resource "aws_api_gateway_integration" "entry_integration" {
  rest_api_id             = aws_api_gateway_rest_api.parking_api.id
  resource_id             = aws_api_gateway_resource.entry_resource.id
  http_method             = aws_api_gateway_method.entry_post.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.entry_lambda.invoke_arn
}

# Integration for /exit
resource "aws_api_gateway_integration" "exit_integration" {
  rest_api_id             = aws_api_gateway_rest_api.parking_api.id
  resource_id             = aws_api_gateway_resource.exit_resource.id
  http_method             = aws_api_gateway_method.exit_post.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.exit_lambda.invoke_arn
}

# Lambda permissions for API Gateway
resource "aws_lambda_permission" "entry_lambda_permission" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.entry_lambda.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.parking_api.execution_arn}/*/*"
}

resource "aws_lambda_permission" "exit_lambda_permission" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.exit_lambda.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.parking_api.execution_arn}/*/*"
} 