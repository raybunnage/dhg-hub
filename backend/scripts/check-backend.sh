#!/bin/bash

# Color codes for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=== FastAPI Backend Setup Checker ==="
echo

# Check Python installation
echo "Checking Python installation..."
if command -v python3 &>/dev/null; then
    echo -e "${GREEN}[OK]${NC} Python3 installed: $(python3 --version)"
else
    echo -e "${RED}[ERROR]${NC} Python3 is not installed"
fi
echo

# Check pip installation
echo "Checking pip installation..."
if command -v pip3 &>/dev/null; then
    echo -e "${GREEN}[OK]${NC} pip3 installed: $(pip3 --version)"
else
    echo -e "${RED}[ERROR]${NC} pip3 is not installed"
fi
echo

# Check virtual environment
echo "Checking virtual environment..."
if [ -d "venv" ]; then
    echo -e "${GREEN}[OK]${NC} Virtual environment exists"
else
    echo -e "${YELLOW}[WARNING]${NC} Virtual environment not found. Creating one..."
    python3 -m venv venv
    echo -e "${GREEN}[OK]${NC} Virtual environment created"
fi
echo

# Activate virtual environment
source venv/bin/activate 2>/dev/null || {
    echo -e "${RED}[ERROR]${NC} Failed to activate virtual environment"
    exit 1
}

# Check FastAPI installation
echo "Checking FastAPI installation..."
if pip list | grep -i "fastapi" &>/dev/null; then
    echo -e "${GREEN}[OK]${NC} FastAPI is installed"
else
    echo -e "${YELLOW}[WARNING]${NC} FastAPI not found. Installing..."
    pip install fastapi
fi
echo

# Check Uvicorn installation
echo "Checking Uvicorn installation..."
if pip list | grep -i "uvicorn" &>/dev/null; then
    echo -e "${GREEN}[OK]${NC} Uvicorn is installed"
else
    echo -e "${YELLOW}[WARNING]${NC} Uvicorn not found. Installing..."
    pip install uvicorn
fi
echo

# Check requirements.txt
echo "Checking requirements.txt..."
if [ -f "requirements.txt" ]; then
    echo -e "${GREEN}[OK]${NC} requirements.txt exists"
else
    echo -e "${YELLOW}[WARNING]${NC} requirements.txt not found. Creating..."
    pip freeze > requirements.txt
    echo -e "${GREEN}[OK]${NC} requirements.txt created"
fi
echo

# Check .env file
echo "Checking environment file..."
if [ -f ".env" ]; then
    echo -e "${GREEN}[OK]${NC} .env file exists"
else
    echo -e "${YELLOW}[WARNING]${NC} .env file not found. Creating template..."
    cat > .env << EOL
DATABASE_URL=your_database_url_here
API_KEY=your_api_key_here
DEBUG=True
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
EOL
    echo -e "${GREEN}[OK]${NC} .env template created"
fi
echo

# Check project structure
echo "Checking project structure..."
for dir in "src" "src/api" "src/models" "src/schemas" "src/services" "tests"; do
    if [ -d "$dir" ]; then
        echo -e "${GREEN}[OK]${NC} $dir directory exists"
    else
        echo -e "${YELLOW}[WARNING]${NC} Creating $dir directory..."
        mkdir -p "$dir"
    fi
done
echo

# Create main.py if it doesn't exist
if [ ! -f "src/main.py" ]; then
    echo "Creating basic main.py template..."
    cat > src/main.py << EOL
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
</code_block_to_apply_changes_from>
