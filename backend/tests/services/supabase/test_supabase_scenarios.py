"""
Development tests for Supabase service scenarios.
These tests are not yet ready for pytest integration.
"""

from dotenv import load_dotenv
import asyncio
import os
from pathlib import Path
import sys
import pytest
from unittest.mock import Mock, patch

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


def test_supabase_service(monkeypatch):
    """Test SupabaseService initialization with mocked client."""
    # Create mock client
    mock_client = Mock()

    # Mock create_client instead of get_supabase
    monkeypatch.setattr(
        "dhg.services.supabase.service.create_client", lambda url, key: mock_client
    )

    # Test service initialization
    service = SupabaseService("test-url", "test-key")
    assert service is not None
    assert service.client == mock_client

    # Test service initialization with no params (should use get_supabase)
    with patch("dhg.core.supabase_client.get_supabase", return_value=mock_client):
        service = SupabaseService()
        assert service is not None
        assert service.client == mock_client
