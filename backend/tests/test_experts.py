from datetime import datetime
from pathlib import Path
import sys
import os
from dotenv import load_dotenv
import pytest
import pytest_asyncio
import asyncio

project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)
from dhg.services.supabase.service import SupabaseService
from dhg.db.experts import Experts

from src.services.exceptions import (
    SupabaseConnectionError,
    SupabaseQueryError,
    SupabaseAuthenticationError,
    SupabaseAuthorizationError,
    SupabaseError,
    SupabaseStorageError,
    map_storage_error,
)


@pytest_asyncio.fixture
async def experts_service():
    """Fixture to create and clean up an Experts service instance."""
    load_dotenv()

    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    email = os.getenv("TEST_EMAIL")
    password = os.getenv("TEST_PASSWORD")
    domain_id = os.getenv("SUPABASE_DOMAIN_ID")

    if not supabase_url or not supabase_key:
        pytest.skip("SUPABASE_URL and SUPABASE_KEY must be set in environment")

    supabase = SupabaseService(url=supabase_url, api_key=supabase_key)
    experts = Experts(supabase, email=email, password=password, domain_id=domain_id)

    yield experts

    # Cleanup after tests
    await experts._cleanup_test_data()


@pytest.mark.asyncio
async def test_crud_operations(experts_service):
    """Test basic CRUD operations for Experts."""
    try:
        # Clean up any existing test data first
        await experts_service._cleanup_test_data()

        # Test data
        test_expert = {
            "expert_name": "test_expert",
            "full_name": "Test Expert",
            "email_address": "test@example.com",
            "is_in_core_group": True,
            "domain_id": "752f3bf7-a392-4283-bd32-e3f0e530c205",
        }

        # Create
        created_expert = await experts_service.add(test_expert)
        assert created_expert is not None
        expert_record = created_expert.records[0]
        assert expert_record["expert_name"] == test_expert["expert_name"]

        # ... rest of test code ...

    finally:
        # Ensure cleanup happens even if test fails
        await experts_service._cleanup_test_data()


@pytest.mark.asyncio
async def test_validation(experts_service):
    """Test validation logic for Experts."""
    try:
        # Clean up any existing test data first
        await experts_service._cleanup_test_data()

        # Test missing required field
        invalid_expert = {
            "expert_name": "test_expert",
            # Missing required field: is_in_core_group
            "domain_id": "test_domain_id",
        }

        with pytest.raises(SupabaseQueryError) as exc_info:
            await experts_service.add(invalid_expert)
        assert "Missing required field" in str(exc_info.value)

        # ... rest of test code ...

    finally:
        # Ensure cleanup happens even if test fails
        await experts_service._cleanup_test_data()


@pytest.mark.asyncio
async def test_aliases(experts_service):
    """Test alias-related operations."""
    try:
        # Clean up any existing test data first
        await experts_service._cleanup_test_data()

        # Create test expert
        test_expert = {
            "expert_name": "test_alias_expert",
            "is_in_core_group": True,
            "domain_id": "752f3bf7-a392-4283-bd32-e3f0e530c205",
            "email_address": "test.alias@example.com",
        }
        created_expert = await experts_service.add(test_expert)
        expert_record = created_expert.records[0]

        # ... rest of test code ...

    finally:
        # Ensure cleanup happens even if test fails
        await experts_service._cleanup_test_data()
