#!/bin/bash

# Lambda Function Packaging Script
# This script packages the Python Lambda function with dependencies

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
SRC_DIR="$PROJECT_ROOT/src"
DIST_DIR="$PROJECT_ROOT/dist"

echo -e "${GREEN}Packaging Lambda function...${NC}"

# Create dist directory if it doesn't exist
mkdir -p "$DIST_DIR"

# Remove existing package
rm -f "$DIST_DIR/lambda_function.zip"

# Create a temporary directory for packaging
TEMP_DIR=$(mktemp -d)
echo -e "${YELLOW}Using temporary directory: $TEMP_DIR${NC}"

# Copy source code
cp -r "$SRC_DIR"/* "$TEMP_DIR/"

# Install dependencies
cd "$TEMP_DIR"
echo -e "${YELLOW}Installing dependencies...${NC}"
pip install -r "$PROJECT_ROOT/requirements.txt" -t . --no-deps

# Create the zip file
echo -e "${YELLOW}Creating zip package...${NC}"
zip -r "$DIST_DIR/lambda_function.zip" . -x "*.pyc" "*__pycache__*" "*.git*"

# Clean up temp directory
rm -rf "$TEMP_DIR"

# Show package info
PACKAGE_SIZE=$(du -h "$DIST_DIR/lambda_function.zip" | cut -f1)
echo -e "${GREEN}Lambda package created successfully!${NC}"
echo -e "${GREEN}Package location: $DIST_DIR/lambda_function.zip${NC}"
echo -e "${GREEN}Package size: $PACKAGE_SIZE${NC}" 