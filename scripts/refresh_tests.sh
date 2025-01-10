#!/bin/bash

# Clear all Python cache
echo "Clearing Python cache..."
find . -type d -name "__pycache__" -exec rm -r {} +
find . -type f -name "*.pyc" -delete

# Clear pytest cache
echo "Clearing pytest cache..."
rm -rf .pytest_cache

# Clear Flask cache (if any exists)
echo "Clearing Flask cache..."
rm -rf instance/

# Force reload environment variables (if using .env)
if [ -f .env ]; then
    source .env
fi

# Run tests with coverage
echo "Running tests..."
PYTHONPATH=. pytest --cache-clear --cov=backend/src --cov-report=term-missing backend/tests -v

# Optional: Run specific test file
# PYTHONPATH=. pytest --cache-clear backend/tests/unit/test_supabase_service.py -v 