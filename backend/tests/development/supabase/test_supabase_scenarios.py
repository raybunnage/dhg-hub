"""
Development tests for Supabase service scenarios.
These tests are not yet ready for pytest integration.
"""

from dotenv import load_dotenv
import asyncio
import os
from pathlib import Path
import sys

# Add the src directory to Python path
project_root = Path(__file__).parent.parent.parent.parent  # Go up to backend/
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from dhg.core.exceptions import (
    SupabaseOperationalError,
    UserNotFoundError,
    InvalidCredentialsError,
)
from dhg.services.supabase.service import SupabaseService


def test_supabase_service():
    service = SupabaseService()
    assert service is not None
