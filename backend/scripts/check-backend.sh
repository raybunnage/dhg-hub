#!/bin/bash

# Color codes for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Initialize error tracking
errors=0
warnings=0

# Function to log errors but continue
log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
    ((errors++))
}

# Function to log warnings
log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
    ((warnings++))
}

echo "=== FastAPI Backend Setup Checker ==="
echo

# Check Python installation
echo "Checking Python installation..."
if command -v python3 &>/dev/null; then
    PYTHON_VERSION=$(python3 --version)
    if [[ $PYTHON_VERSION =~ ^Python\ 3\.[0-9]+\.[0-9]+$ ]]; then
        echo -e "${GREEN}[OK]${NC} Python3 installed: $PYTHON_VERSION"
    else
        log_warning "Python version format unexpected: $PYTHON_VERSION"
    fi
else
    log_error "Python3 is not installed"
fi
echo

# Check pip installation
echo "Checking pip installation..."
if command -v pip3 &>/dev/null; then
    echo -e "${GREEN}[OK]${NC} pip3 installed: $(pip3 --version)"
else
    log_error "pip3 is not installed"
fi
echo

# Check virtual environment (without creating)
echo "Checking virtual environment..."
if [ -d ".venv" ]; then
    if [ -f ".venv/bin/activate" ]; then
        echo -e "${GREEN}[OK]${NC} Virtual environment exists and appears valid"
    else
        log_error "Virtual environment exists but may be corrupted (missing activate script)"
    fi
else
    log_error "Virtual environment not found. Please create one manually with 'python3 -m venv .venv'"
fi
echo

# Try to activate virtual environment but continue if it fails
echo "Attempting to activate virtual environment..."
if source .venv/bin/activate 2>/dev/null; then
    echo -e "${GREEN}[OK]${NC} Virtual environment activated"
else
    log_error "Failed to activate virtual environment - continuing with system Python"
fi
echo

# Check critical dependencies
echo "Checking critical dependencies..."
PACKAGES=(
    "fastapi"
    "uvicorn"
    "pydantic"
    "sqlalchemy"
    "python-jose"
    "python-dotenv"
    "email-validator"
    "pytest"
    "black"
    "flake8"
    "mypy"
)

for package in "${PACKAGES[@]}"; do
    if pip list 2>/dev/null | grep -i "^$package" &>/dev/null; then
        echo -e "${GREEN}[OK]${NC} $package is installed"
    else
        log_error "$package is not installed"
    fi
done
echo

# Check project structure
echo "Checking project structure..."
for dir in "src" "src/api" "src/models" "src/schemas" "src/services" "tests"; do
    if [ -d "$dir" ]; then
        echo -e "${GREEN}[OK]${NC} $dir directory exists"
    else
        log_warning "$dir directory missing"
    fi
done
echo

# Check .env file
echo "Checking environment file..."
if [ -f ".env" ]; then
    echo -e "${GREEN}[OK]${NC} .env file exists"
else
    log_error ".env file not found"
fi
echo

# Check development tools
echo "Checking development tools..."
if command -v git &>/dev/null; then
    echo -e "${GREEN}[OK]${NC} Git installed: $(git --version)"
else
    log_warning "Git not installed"
fi

if command -v docker &>/dev/null; then
    echo -e "${GREEN}[OK]${NC} Docker installed: $(docker --version)"
else
    log_warning "Docker not installed (optional)"
fi
echo

# Print summary
echo "=== Check Summary ==="
if [ $errors -gt 0 ]; then
    echo -e "${RED}Found $errors error(s)${NC}"
fi
if [ $warnings -gt 0 ]; then
    echo -e "${YELLOW}Found $warnings warning(s)${NC}"
fi
if [ $errors -eq 0 ] && [ $warnings -eq 0 ]; then
    echo -e "${GREEN}All checks passed successfully!${NC}"
fi
echo
