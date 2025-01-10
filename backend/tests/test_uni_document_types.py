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
from services.supabase.service import SupabaseService
from src.db.uni_document_types import UniDocumentTypes

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
async def document_types_service():
    """Fixture to create and clean up a UniDocumentTypes service instance."""
    load_dotenv()

    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    email = os.getenv("TEST_EMAIL")
    password = os.getenv("TEST_PASSWORD")
    domain_id = os.getenv("SUPABASE_DOMAIN_ID")

    if not supabase_url or not supabase_key:
        pytest.skip("SUPABASE_URL and SUPABASE_KEY must be set in environment")

    supabase = SupabaseService(url=supabase_url, api_key=supabase_key)
    doc_types = UniDocumentTypes(
        supabase, email=email, password=password, domain_id=domain_id
    )

    yield doc_types

    # Cleanup after tests
    await doc_types._cleanup_test_data()


@pytest.mark.asyncio
async def test_crud_operations(document_types_service):
    """Test basic CRUD operations for UniDocumentTypes."""
    try:
        # Clean up any existing test data first
        await document_types_service._cleanup_test_data()

        # Test data
        test_doc_type = {
            "document_type": "test_document_type",
            "category": "test_category",
            "is_ai_generated": False,
            "domain_id": "752f3bf7-a392-4283-bd32-e3f0e530c205",
        }

        # Create
        created_doc = await document_types_service.add(test_doc_type)
        assert created_doc is not None
        assert created_doc.count == 1
        assert len(created_doc.records) == 1
        doc_record = created_doc.records[0]
        assert doc_record["document_type"] == test_doc_type["document_type"]

        # Read by ID
        retrieved_doc = await document_types_service.get_by_id(doc_record["id"])
        assert retrieved_doc is not None
        assert retrieved_doc["document_type"] == test_doc_type["document_type"]

        # Read by name
        name_retrieved_doc = await document_types_service.get_by_name(
            test_doc_type["document_type"]
        )
        assert name_retrieved_doc is not None
        assert name_retrieved_doc["id"] == doc_record["id"]

        # Update
        update_data = {
            "category": "updated_test_category",
        }
        updated_doc = await document_types_service.update(doc_record["id"], update_data)
        assert updated_doc is not None
        assert updated_doc["category"] == update_data["category"]

        # Get all with filters
        all_docs = await document_types_service.get_all(
            fields=["id", "document_type", "category"],
            where_filters=[("document_type", "eq", test_doc_type["document_type"])],
        )
        assert all_docs is not None
        assert len(all_docs) > 0
        assert any(doc["id"] == doc_record["id"] for doc in all_docs)

        # Delete
        deleted = await document_types_service.delete(doc_record["id"])
        assert deleted is not None

        # Verify deletion
        with pytest.raises(SupabaseQueryError):
            await document_types_service.get_by_id(doc_record["id"])

    finally:
        await document_types_service._cleanup_test_data()


@pytest.mark.asyncio
async def test_validation(document_types_service):
    """Test validation logic for UniDocumentTypes."""
    try:
        # Test missing required field
        invalid_doc = {
            "document_type": "test_doc",
            # Missing required fields: category, is_ai_generated, domain_id
        }

        with pytest.raises(SupabaseQueryError) as exc_info:
            await document_types_service.add(invalid_doc)
        assert "Missing required field" in str(exc_info.value)

        # Test invalid type
        invalid_type_doc = {
            "document_type": "test_doc",
            "category": "test",
            "is_ai_generated": "not_a_boolean",  # Should be boolean
            "domain_id": "test_domain_id",
        }

        with pytest.raises(SupabaseQueryError) as exc_info:
            await document_types_service.add(invalid_type_doc)
        assert "must be a bool" in str(exc_info.value)

    finally:
        await document_types_service._cleanup_test_data()


@pytest.mark.asyncio
async def test_aliases(document_types_service):
    """Test alias-related operations."""
    try:
        # Clean up any existing test data first
        await document_types_service._cleanup_test_data()

        # Create test document type
        test_doc = {
            "document_type": "test_alias_doc",
            "category": "test_category",
            "is_ai_generated": False,
            "domain_id": "752f3bf7-a392-4283-bd32-e3f0e530c205",
        }
        created_doc = await document_types_service.add(test_doc)
        assert created_doc is not None
        assert created_doc.count == 1
        doc_record = created_doc.records[0]

        # Add alias
        alias_name = "test_alias"
        added_alias = await document_types_service.add_alias(
            "test_alias_doc", alias_name
        )
        assert added_alias is not None
        assert added_alias.count == 1
        alias_record = added_alias.records[0]

        # Get aliases
        aliases = await document_types_service.get_aliases("test_alias_doc")
        assert aliases is not None and len(aliases) > 0
        assert any(a["alias_name"] == alias_name for a in aliases)

        # Delete alias
        deleted = await document_types_service.delete_alias(alias_record["id"])
        assert deleted is True

    finally:
        await document_types_service._cleanup_test_data()
