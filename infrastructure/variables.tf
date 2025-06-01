variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "eu-north-1"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "parking-lot-system"
}

variable "table_name" {
  description = "DynamoDB table name for parking tickets"
  type        = string
  default     = "parking-tickets"
}

variable "hourly_rate" {
  description = "Parking fee per hour in USD"
  type        = string
  default     = "10.0"
}

variable "billing_increment_minutes" {
  description = "Billing increment in minutes"
  type        = string
  default     = "15"
}

variable "log_retention_days" {
  description = "CloudWatch log retention in days"
  type        = number
  default     = 14
} 