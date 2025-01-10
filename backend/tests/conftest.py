import pytest
import os
from pathlib import Path


@pytest.fixture(autouse=True)
def setup_test_env():
    """Setup test environment variables."""
    os.environ["SUPABASE_URL"] = "https://your-project.supabase.co"
    os.environ["SUPABASE_KEY"] = "your-anon-key"
    yield
