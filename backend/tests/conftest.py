import pytest
import sys
import os
from pathlib import Path

# Add the backend/src directory to the Python path
backend_src = Path(__file__).parent.parent / "src"
sys.path.append(str(backend_src))

# Now we can safely import our modules
from dhg.core.config import settings


@pytest.fixture(autouse=True)
def setup_test_env():
    """Setup test environment variables."""
    os.environ["SUPABASE_URL"] = "http://test-url"
    os.environ["SUPABASE_KEY"] = "test-key"
    yield
