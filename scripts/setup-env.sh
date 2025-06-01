#!/bin/bash

# Environment Setup Script
# This script sets up the development environment

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Setting up Parking Lot Management System development environment${NC}"

# Check if Python 3.12 is available
if ! command -v python3.12 &> /dev/null; then
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}ERROR: Python 3 is not installed. Please install Python 3.12+${NC}"
        exit 1
    fi
    PYTHON_CMD="python3"
else
    PYTHON_CMD="python3.12"
fi

echo -e "${YELLOW}Using Python: $($PYTHON_CMD --version)${NC}"

# Create virtual environment
echo -e "${YELLOW}Creating virtual environment...${NC}"
$PYTHON_CMD -m venv venv

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate

# Upgrade pip
echo -e "${YELLOW}Upgrading pip...${NC}"
pip install --upgrade pip

# Install development dependencies
echo -e "${YELLOW}Installing development dependencies...${NC}"
pip install -r requirements-dev.txt

# Install pre-commit hooks
echo -e "${YELLOW}Installing pre-commit hooks...${NC}"
pre-commit install

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo -e "${YELLOW}Creating .env file from template...${NC}"
    cp .env.example .env 2>/dev/null || echo "# Environment variables" > .env
    echo -e "${BLUE}Please edit .env file with your AWS configuration${NC}"
fi

echo -e "${GREEN}Development environment setup complete!${NC}"
echo -e "${BLUE}Next steps:${NC}"
echo -e "1. Activate virtual environment: ${YELLOW}source venv/bin/activate${NC}"
echo -e "2. Configure AWS credentials: ${YELLOW}aws configure${NC}"
echo -e "3. Edit .env file with your settings"
echo -e "4. Run tests: ${YELLOW}pytest${NC}"
echo -e "5. Deploy: ${YELLOW}./scripts/deploy.sh${NC}" 