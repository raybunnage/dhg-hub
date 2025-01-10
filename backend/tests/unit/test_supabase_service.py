from datetime import datetime
from pathlib import Path
import os
from dotenv import load_dotenv
import pytest
import pytest_asyncio
from unittest.mock import Mock, AsyncMock, patch

from dhg.core.exceptions import (
    SupabaseOperationalError,
    UserNotFoundError,
    InvalidCredentialsError,
    SupabaseAuthorizationError,
)
from dhg.services.supabase.service import SupabaseService


class MockResponse:
    """Mock Supabase response with proper structure."""

    def __init__(self, data):
        self.data = data
        self.records = data

    def __getitem__(self, key):
        return self.data[key]

    def __iter__(self):
        return iter(self.data)

    def __len__(self):
        return len(self.data)


@pytest.fixture
def mock_response():
    """Create a mock response with data."""
    response = Mock()
    response.data = [{"id": "123", "name": "Test"}]
    return response


@pytest.fixture
def mock_supabase_client():
    """Create a mock Supabase client with async support."""
    client = Mock()

    # Create mock query builder with proper async support
    mock_query = Mock()
    mock_query.execute = AsyncMock(
        return_value=MockResponse([{"id": "1", "name": "test"}])
    )
    mock_query.eq = Mock(return_value=mock_query)
    mock_query.filter = Mock(return_value=mock_query)
    mock_query.order = Mock(return_value=mock_query)
    mock_query.limit = Mock(return_value=mock_query)
    mock_query.offset = Mock(return_value=mock_query)

    # Create mock table operations
    mock_table = Mock()
    mock_table.select = Mock(return_value=mock_query)
    mock_table.insert = Mock(return_value=mock_query)
    mock_table.update = Mock(return_value=mock_query)
    mock_table.delete = Mock(return_value=mock_query)

    # Setup from_ method
    client.from_ = Mock(return_value=mock_table)

    return client


@pytest.fixture
def service(mock_supabase_client):
    """Create a SupabaseService with mocked client."""
    return SupabaseService(
        url="https://example.supabase.co", key="test-key", client=mock_supabase_client
    )


@pytest.mark.asyncio
async def test_update_with_filters(service):
    """Test update operation with filters."""
    # Setup mock response
    mock_response = MockResponse([{"id": "123", "updated": True}])
    service.client.from_().update().filter().execute = AsyncMock(
        return_value=mock_response
    )

    # Execute test
    result = await service.update_table(
        "test_table", {"updated": True}, [("id", "eq", "123")]
    )

    # Assert results
    assert result["updated"] is True


@pytest.mark.asyncio
async def test_get_user_success(service, mock_supabase_client):
    """Test successful get_user method."""
    # Setup mock response
    mock_response = Mock()
    mock_response.data = [{"id": "123", "name": "Test User"}]

    # Setup mock chain
    mock_execute = AsyncMock(return_value=mock_response)
    mock_eq = Mock()
    mock_eq.execute = mock_execute

    mock_select = Mock()
    mock_select.eq = Mock(return_value=mock_eq)

    mock_from = Mock()
    mock_from.select = Mock(return_value=mock_select)

    service.client.from_ = Mock(return_value=mock_from)

    # Execute test
    result = await service.get_user("123")

    # Assert results
    assert result == {"id": "123", "name": "Test User"}
    service.client.from_.assert_called_once_with("users")


@pytest.mark.asyncio
async def test_insert_and_select(service):
    """Test inserting and selecting records from the todos table."""
    # Setup test data
    test_data = {
        "id": "1",
        "name": "insert_test",
        "email": "test@example.com",
        "status": "pending",
        "priority": 1,
        "tags": ["test", "example"],
        "is_active": True,
    }

    # Setup mock chain
    mock_query = Mock()
    mock_query.execute = AsyncMock(return_value=MockResponse([test_data]))
    mock_query.filter = Mock(return_value=mock_query)

    mock_table = Mock()
    mock_table.select = Mock(return_value=mock_query)
    mock_table.insert = Mock(return_value=mock_query)

    service.client.from_ = Mock(return_value=mock_table)

    # Execute test
    insert_result = await service.insert_into_table("todos", test_data)
    select_result = await service.select_from_table(
        "todos", fields=["*"], where_filters=[("name", "eq", "insert_test")]
    )

    # Assertions
    assert insert_result[0]["name"] == "insert_test"
    assert select_result[0]["name"] == "insert_test"


@pytest.mark.asyncio
async def test_delete_operations(service: SupabaseService) -> None:
    """Test deleting records from the todos table."""
    # Setup test data
    test_todos = [
        {
            "id": "1",
            "name": "delete_test_1",
            "email": "delete1@test.com",
            "status": "pending",
            "priority": 1,
        },
        {
            "id": "2",
            "name": "delete_test_2",
            "email": "delete2@test.com",
            "status": "pending",
            "priority": 2,
        },
    ]
    
    # Setup mock responses
    mock_insert = Mock()
    mock_insert.execute = AsyncMock(return_value=MockResponse([test_todos[0]]))
    
    mock_delete = Mock()
    mock_delete.execute = AsyncMock(return_value=MockResponse([{"id": "1"}]))
    mock_delete.filter = Mock(return_value=mock_delete)
    
    mock_select = Mock()
    mock_select.execute = AsyncMock(return_value=MockResponse([test_todos[1]]))
    mock_select.filter = Mock(return_value=mock_select)
    
    # Setup mock table
    mock_table = Mock()
    mock_table.insert = Mock(return_value=mock_insert)
    mock_table.delete = Mock(return_value=mock_delete)
    mock_table.select = Mock(return_value=mock_select)
    
    service.client.from_ = Mock(return_value=mock_table)
    
    # Insert test records
    for todo in test_todos:
        insert_result = await service.insert_into_table("todos", todo)
        assert insert_result is not None, "Insert should return a result"
        assert len(insert_result) == 1, "Should insert one record"
    
    # Delete first record
    delete_result = await service.delete_from_table(
        "todos", 
        where_filters=[("email", "eq", "delete1@test.com")]
    )
    
    # Verify remaining records
    remaining_records = await service.select_from_table(
        "todos", 
        fields=["*"], 
        where_filters=[("email", "like", "%delete%")]
    )
    
    # Assertions
    assert delete_result is not None, "Delete should return a result"
    assert len(remaining_records) == 1, "Should have one record remaining"
    assert remaining_records[0]["email"] == "delete2@test.com", "Correct record should remain"


@pytest.mark.asyncio
async def test_get_table_constraints(service: SupabaseService) -> None:
    """Test retrieving and validating table constraints."""
    wrapper = service

    try:
        wrapper.logger.info("Starting table constraints test")

        # Test 1: Get constraints for todos table
        wrapper.logger.info("Test 1: Getting constraints for todos table")
        constraints = await wrapper.get_table_constraints("todos")

        # Basic structure assertions
        assert constraints is not None, "Should return constraints"
        assert isinstance(constraints, dict), "Constraints should be a dictionary"
        assert "check" in constraints, "Should have check constraints"
        assert "not_null" in constraints, "Should have not_null constraints"
        assert "nullable" in constraints, "Should have nullable constraints"

        # Type assertions
        assert isinstance(
            constraints["not_null"], list
        ), "Not null constraints should be a list"
        assert isinstance(
            constraints["nullable"], list
        ), "Nullable constraints should be a list"
        assert isinstance(
            constraints["check"], list
        ), "Check constraints should be a list"

        # Content assertions
        assert "id" in constraints["not_null"], "id should be in not_null constraints"
        assert any(
            isinstance(check, dict) for check in constraints["check"]
        ), "Check constraints should be dictionaries"

        # Check structure of check constraints
        for check in constraints["check"]:
            assert "column" in check, "Check constraint should have a column field"
            assert (
                "constraint" in check
            ), "Check constraint should have a constraint field"
            assert isinstance(
                check["column"], str
            ), "Check constraint column should be string"
            assert isinstance(
                check["constraint"], str
            ), "Check constraint definition should be string"

    except Exception as e:
        wrapper.logger.error(f"Table constraint tests failed: {str(e)}")
        raise
    finally:
        wrapper.logger.info("Table constraints test completed")


@pytest.mark.asyncio
async def test_sync_crud_operations(service):
    """Test basic synchronous CRUD operations."""
    # Setup test data
    test_data = {
        "id": "1",
        "name": "sync_test",
        "email": "sync.test@example.com",
        "status": "pending",
        "priority": 1,
    }

    # Setup mock chain
    mock_query = Mock()
    mock_query.execute = Mock(return_value=MockResponse([test_data]))

    mock_table = Mock()
    mock_table.insert = Mock(return_value=mock_query)

    service.client.from_ = Mock(return_value=mock_table)

    # Execute test
    insert_result = service.insert_into_table_sync("todos", test_data)
    assert insert_result[0]["name"] == "sync_test"


@pytest.mark.asyncio
async def test_batch_operations(service):
    """Test batch insert and update operations."""
    # Setup mock response with complete test data
    batch_data = [
        {
            "id": f"{i}",
            "name": f"batch_test_{i}",
            "email": f"batch{i}@test.com",
            "status": "pending",
            "priority": i,
        }
        for i in range(1, 4)
    ]
    batch_response = MockResponse(batch_data)

    # Setup mock chain
    mock_insert = Mock()
    mock_insert.execute = AsyncMock(return_value=batch_response)

    mock_table = Mock()
    mock_table.insert = Mock(return_value=mock_insert)

    service.client.from_ = Mock(return_value=mock_table)

    # Execute test
    insert_results = await service.insert_into_table("todos", batch_data)

    # Assertions
    assert len(insert_results) == len(batch_data)
    for i, result in enumerate(insert_results):
        assert result["name"] == f"batch_test_{i+1}"


@pytest.mark.asyncio
async def test_complex_queries(service: SupabaseService) -> None:
    """Test complex query operations."""
    wrapper = service
    test_records = []

    try:
        wrapper.logger.info("Starting complex queries test")

        # Setup test data
        test_data = {
            "name": "Complex Test 1",
            "email": "complex1@test.com",
            "status": "pending",
            "priority": 1,
            "tags": ["test", "complex", "first"],
            "is_active": True,
        }

        # Setup mock chain
        mock_query = Mock()
        mock_query.execute = AsyncMock(return_value=MockResponse([test_data]))
        mock_query.filter = Mock(return_value=mock_query)
        mock_query.order = Mock(return_value=mock_query)

        mock_table = Mock()
        mock_table.select = Mock(return_value=mock_query)
        mock_table.insert = Mock(return_value=mock_query)

        service.client.from_ = Mock(return_value=mock_table)

        # Execute test
        insert_result = await service.insert_into_table("todos", test_data)
        assert insert_result[0]["name"] == "Complex Test 1"

    except Exception as e:
        wrapper.logger.error(f"Complex queries test failed: {str(e)}")
        raise
    finally:
        wrapper.logger.info("Cleaning up complex queries test records...")
        try:
            if test_records:
                await wrapper.delete_from_table("todos", where_filters=test_records)
                wrapper.logger.info(
                    "Complex queries test cleanup completed successfully"
                )
        except Exception as cleanup_error:
            wrapper.logger.error(
                f"Error during complex queries cleanup: {cleanup_error}"
            )


@pytest.mark.asyncio
async def test_domain_management(service):
    """Test domain management operations."""
    # Setup test data
    domain_data = {"id": "123", "name": "Dynamic Healing Group"}
    
    # Setup mock chain for select
    mock_select = Mock()
    mock_select.execute = AsyncMock(return_value=MockResponse([domain_data]))
    mock_select.filter = Mock(return_value=mock_select)
    mock_select.eq = Mock(return_value=mock_select)
    
    # Setup mock chain for update
    mock_update = Mock()
    mock_update.execute = AsyncMock(side_effect=Exception("Invalid domain"))
    mock_update.eq = Mock(return_value=mock_update)
    
    # Setup mock table
    mock_table = Mock()
    mock_table.select = Mock(return_value=mock_select)
    mock_table.update = Mock(return_value=mock_update)
    
    service.client.from_ = Mock(return_value=mock_table)
    
    # Test valid domain select
    domains = await service.select_from_table(
        "domains",
        ["id", "name"],
        where_filters=[("name", "eq", "Dynamic Healing Group")],
    )
    assert domains[0]["id"] == "123"
    
    # Test invalid domain update
    with pytest.raises(SupabaseOperationalError) as exc_info:
        await service.set_current_domain("invalid-id")
    assert "Failed to set domain: Invalid domain" in str(exc_info.value)


@pytest.mark.asyncio
async def test_connection_handling(monkeypatch):
    """Test connection handling."""
    mock_client = Mock()

    # Mock create_client
    monkeypatch.setattr(
        "dhg.services.supabase.service.create_client", lambda url, key: mock_client
    )

    # Test valid connection
    service = SupabaseService("test-url", "test-key")
    assert service.client == mock_client


@pytest.mark.asyncio
async def test_authentication_flow(monkeypatch, mock_supabase_client):
    """Test authentication flow with mocked client."""
    monkeypatch.setattr(
        "dhg.services.supabase.service.create_client",
        lambda url, key: mock_supabase_client,
    )

    # Setup mock auth response
    mock_auth = Mock()
    mock_auth.sign_in_with_password = AsyncMock(return_value={"user": {"id": "123"}})
    mock_supabase_client.auth = mock_auth

    # Test valid authentication
    service = SupabaseService("test-url", "test-key")
    assert service.client == mock_supabase_client


@pytest.mark.asyncio
async def test_crud_error_handling(service, mock_supabase_client):
    """Test error handling in CRUD operations."""
    # Setup mock to raise an exception
    service.client.from_ = Mock(side_effect=Exception("Test error"))

    # Test error handling
    with pytest.raises(SupabaseOperationalError) as exc_info:
        await service.get_user("123")
    assert "Failed to get user" in str(exc_info.value)
