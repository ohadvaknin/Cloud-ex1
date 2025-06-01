#!/bin/bash

# Parking Lot Management System - Deployment Script
# This script deploys the Lambda functions and infrastructure to AWS

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
INFRASTRUCTURE_DIR="$PROJECT_ROOT/infrastructure"
SRC_DIR="$PROJECT_ROOT/src"
DIST_DIR="$PROJECT_ROOT/dist"

echo -e "${GREEN}🚀 Starting deployment of Parking Lot Management System${NC}"

# Check prerequisites
echo -e "${YELLOW}📋 Checking prerequisites...${NC}"

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo -e "${RED}❌ AWS CLI is not installed. Please install it first.${NC}"
    exit 1
fi

# Check if Terraform is installed
if ! command -v terraform &> /dev/null; then
    echo -e "${RED}❌ Terraform is not installed. Please install it first.${NC}"
    exit 1
fi

# Check AWS credentials
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}❌ AWS credentials not configured. Please run 'aws configure' first.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisites check passed${NC}"

# Create dist directory if it doesn't exist
mkdir -p "$DIST_DIR"

# Package Lambda function
echo -e "${YELLOW}📦 Packaging Lambda function...${NC}"
cd "$SRC_DIR"

# Create a temporary directory for packaging
TEMP_DIR=$(mktemp -d)
cp -r . "$TEMP_DIR/"

# Install dependencies in the temp directory
cd "$TEMP_DIR"
pip install -r "$PROJECT_ROOT/requirements.txt" -t .

# Create the zip file
cd "$TEMP_DIR"
zip -r "$DIST_DIR/lambda_function.zip" . -x "*.pyc" "*__pycache__*"

# Clean up temp directory
rm -rf "$TEMP_DIR"

echo -e "${GREEN}✅ Lambda function packaged successfully${NC}"

# Deploy infrastructure with Terraform
echo -e "${YELLOW}🏗️  Deploying infrastructure with Terraform...${NC}"
cd "$INFRASTRUCTURE_DIR"

# Initialize Terraform
terraform init

# Plan the deployment
terraform plan

# Apply the deployment
echo -e "${YELLOW}🚀 Applying Terraform configuration...${NC}"
terraform apply -auto-approve

# Get outputs
echo -e "${GREEN}📋 Deployment completed! Here are your endpoints:${NC}"
API_URL=$(terraform output -raw api_gateway_url)
echo -e "${GREEN}API Gateway URL: ${API_URL}${NC}"
echo -e "${GREEN}Entry Endpoint: ${API_URL}/entry${NC}"
echo -e "${GREEN}Exit Endpoint: ${API_URL}/exit${NC}"

echo -e "${GREEN}🎉 Deployment successful!${NC}"
echo -e "${YELLOW}💡 Test your API with:${NC}"
echo -e "curl -X POST '${API_URL}/entry?plate=ABC123&parkingLot=1'"
echo -e "curl -X POST '${API_URL}/exit?ticketId=<your-ticket-id>'" 