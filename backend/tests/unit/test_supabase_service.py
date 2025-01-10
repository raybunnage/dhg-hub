from datetime import datetime
from pathlib import Path
import os
from dotenv import load_dotenv
import pytest
import pytest_asyncio

from services.exceptions import (
    SupabaseConnectionError,
    SupabaseQueryError,
    SupabaseAuthenticationError,
    SupabaseAuthorizationError,
)
from services.supabase.service import SupabaseService


@pytest_asyncio.fixture
async def supabase_wrapper() -> SupabaseService:
    """Fixture to create SupabaseService instance."""
    load_dotenv()
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    return SupabaseService(url, key)


@pytest.mark.asyncio
async def test_update_with_filters(supabase_wrapper: SupabaseService) -> None:
    """Test updating records with filters in the todos table."""
    wrapper = supabase_wrapper
    test_records = []

    try:
        wrapper.logger.info("Starting update with filters test")

        # Create a test record to update
        test_todo = {
            "name": "update_test",
            "email": "bunnage.ray@gmail.com",
            "status": "pending",
            "priority": 1,
        }
        insert_result = await wrapper.insert_into_table(
            table_name="todos", insert_fields=test_todo
        )
        test_records.append(("email", "ilike", "%bunnage.ray@gmail.com%"))

        # Update todos with email matching pattern
        wrapper.logger.info("Updating todos with email pattern match")
        result = await wrapper.update_table(
            table_name="todos",
            update_fields={"status": "archived", "priority": 2},
            where_filters=[("email", "ilike", "%bunnage.ray@gmail.com%")],
        )

        # Log results
        if result:
            wrapper.logger.info("Successfully updated record")
            wrapper.logger.debug(
                f"""Updated todo details:
                ID: {result.get('id')}
                Name: {result.get('name')}
                Email: {result.get('email')}
                Status: {result.get('status')}
                Created at: {result.get('created_at')}
                """
            )
        else:
            wrapper.logger.info("No records were updated")

        # Reset the status back to pending for future tests
        wrapper.logger.info("Resetting updated records back to pending status")
        reset_result = await wrapper.update_table(
            table_name="todos",
            update_fields={"status": "pending", "priority": 1},
            where_filters=[("email", "ilike", "%bunnage.ray@gmail.com%")],
        )
        wrapper.logger.info("Reset operation completed")

        # Add assertions
        assert result is not None, "Update should return results"
        assert (
            result.get("status") == "archived"
        ), "Status should be updated to archived"
        assert result.get("priority") == 2, "Priority should be updated to 2"

    except Exception as e:
        wrapper.logger.error(f"Error during update with filters test: {str(e)}")
        raise
    finally:
        wrapper.logger.info("Cleaning up test records...")
        try:
            if test_records:
                await wrapper.delete_from_table(
                    table_name="todos", where_filters=test_records
                )
                wrapper.logger.info("Cleanup completed successfully")
        except Exception as cleanup_error:
            wrapper.logger.error(f"Error during cleanup: {cleanup_error}")
        wrapper.logger.info("Completed update with filters test")


@pytest.mark.asyncio
async def test_insert_and_select(supabase_wrapper: SupabaseService) -> None:
    """Test inserting and selecting records from the todos table."""
    wrapper = supabase_wrapper
    test_records = []

    try:
        wrapper.logger.info("Starting insert and select test")

        # Test data
        test_todo = {
            "name": "insert_test",
            "email": "test@example.com",
            "status": "pending",
            "priority": 1,
            "tags": ["test", "example"],
            "is_active": True,
        }

        # Insert test record
        wrapper.logger.info("Inserting test record")
        insert_result = await wrapper.insert_into_table("todos", test_todo)
        test_records.append(("name", "eq", "insert_test"))

        # Select the inserted record
        wrapper.logger.info("Selecting inserted record")
        select_result = await wrapper.select_from_table(
            "todos", fields=["*"], where_filters=[("name", "eq", "insert_test")]
        )

        # Assertions
        assert insert_result is not None, "Insert should return a result"
        assert select_result is not None, "Select should return a result"
        assert len(select_result) > 0, "Select should return at least one record"
        assert (
            select_result[0].get("name") == "insert_test"
        ), "Selected record should match inserted name"
        assert (
            select_result[0].get("email") == "test@example.com"
        ), "Selected record should match inserted email"

    except Exception as e:
        wrapper.logger.error(f"Error during insert and select test: {str(e)}")
        raise
    finally:
        wrapper.logger.info("Cleaning up test records...")
        try:
            if test_records:
                await wrapper.delete_from_table("todos", test_records)
                wrapper.logger.info("Cleanup completed successfully")
        except Exception as cleanup_error:
            wrapper.logger.error(f"Error during cleanup: {cleanup_error}")
        wrapper.logger.info("Completed insert and select test")


@pytest.mark.asyncio
async def test_delete_operations(supabase_wrapper: SupabaseService) -> None:
    """Test deleting records from the todos table."""
    wrapper = supabase_wrapper
    test_records = []

    try:
        wrapper.logger.info("Starting delete operations test")

        # Create test records
        test_todos = [
            {
                "name": "delete_test_1",
                "email": "delete1@test.com",
                "status": "pending",
                "priority": 1,
            },
            {
                "name": "delete_test_2",
                "email": "delete2@test.com",
                "status": "pending",
                "priority": 2,
            },
        ]

        # Insert test records
        for todo in test_todos:
            insert_result = await wrapper.insert_into_table("todos", todo)
            assert insert_result is not None, "Insert should return a result"
            assert len(insert_result.records) == 1, "Should insert one record"
            test_records.append(("email", "like", f"%{todo['email']}%"))

        # Test single record deletion
        wrapper.logger.info("Testing single record deletion")
        delete_result = await wrapper.delete_from_table(
            "todos", where_filters=[("email", "eq", "delete1@test.com")]
        )

        # Verify deletion
        remaining_records = await wrapper.select_from_table(
            "todos", fields=["*"], where_filters=[("email", "like", "%delete%")]
        )

        # Assertions
        assert delete_result is not None, "Delete should return a result"
        assert len(remaining_records) == 1, "Should have one record remaining"
        assert (
            remaining_records[0].get("email") == "delete2@test.com"
        ), "Correct record should remain"

    except Exception as e:
        wrapper.logger.error(f"Error during delete operations test: {str(e)}")
        raise
    finally:
        wrapper.logger.info("Cleaning up any remaining test records...")
        try:
            if test_records:
                await wrapper.delete_from_table("todos", test_records)
                wrapper.logger.info("Cleanup completed successfully")
        except Exception as cleanup_error:
            wrapper.logger.error(f"Error during cleanup: {cleanup_error}")
        wrapper.logger.info("Completed delete operations test")


@pytest.mark.asyncio
async def test_get_table_constraints(supabase_wrapper: SupabaseService) -> None:
    """Test retrieving and validating table constraints."""
    wrapper = supabase_wrapper

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
async def test_sync_crud_operations(supabase_wrapper: SupabaseService) -> None:
    """Test basic synchronous CRUD operations."""
    wrapper = supabase_wrapper
    test_records = []

    try:
        wrapper.logger.info("Starting synchronous CRUD operations test")

        # Test 1: Sync Insert
        test_record = {
            "name": "sync_test",
            "email": "sync.test@example.com",
            "status": "pending",
            "priority": 1,
            "tags": ["sync", "test"],
            "is_active": True,
        }

        insert_result = wrapper.insert_into_table_sync("todos", test_record)
        test_records.append(("name", "eq", "sync_test"))

        assert insert_result is not None, "Sync insert should return result"
        assert (
            insert_result.records[0]["name"] == "sync_test"
        ), "Inserted record should match"

        # Test 2: Sync Select
        select_result = wrapper.select_from_table_sync(
            "todos", fields=["*"], where_filters=[("name", "eq", "sync_test")]
        )

        assert len(select_result) > 0, "Should find inserted record"
        assert (
            select_result[0].get("email") == "sync.test@example.com"
        ), "Selected record should match"

        # Test 3: Sync Update
        update_result = wrapper.update_table_sync(
            "todos",
            update_fields={"status": "completed"},
            where_filters=[("name", "eq", "sync_test")],
        )

        assert update_result.get("status") == "completed", "Status should be updated"

    except Exception as e:
        wrapper.logger.error(f"Synchronous CRUD test failed: {str(e)}")
        raise
    finally:
        wrapper.logger.info("Cleaning up sync test records...")
        try:
            if test_records:
                wrapper.delete_from_table_sync("todos", where_filters=test_records)
                wrapper.logger.info("Sync test cleanup completed successfully")
        except Exception as cleanup_error:
            wrapper.logger.error(f"Error during sync test cleanup: {cleanup_error}")


@pytest.mark.asyncio
async def test_batch_operations(supabase_wrapper: SupabaseService) -> None:
    """Test batch insert and update operations."""
    wrapper = supabase_wrapper
    test_records = []

    try:
        wrapper.logger.info("Starting batch operations test")

        # Test 1: Batch Insert
        batch_records = [
            {
                "name": f"batch_test_{i}",
                "email": f"batch{i}@test.com",
                "status": "pending",
                "priority": i,
                "tags": ["batch", f"test{i}"],
                "is_active": True,
            }
            for i in range(1, 4)
        ]

        insert_results = await wrapper.insert_into_table("todos", batch_records)
        for record in batch_records:
            test_records.append(("name", "like", f"%{record['name']}%"))

        assert len(insert_results.records) == len(
            batch_records
        ), "All records should be inserted"

        # Test 2: Batch Update
        update_result = await wrapper.update_table(
            "todos",
            update_fields={"status": "completed"},
            where_filters=[("name", "like", "%batch_test%")],
        )

        # Verify updates
        updated_records = await wrapper.select_from_table(
            "todos", fields=["*"], where_filters=[("name", "like", "%batch_test%")]
        )

        assert all(
            r["status"] == "completed" for r in updated_records
        ), "All records should be updated"

    except Exception as e:
        wrapper.logger.error(f"Batch operations test failed: {str(e)}")
        raise
    finally:
        wrapper.logger.info("Cleaning up batch test records...")
        try:
            if test_records:
                await wrapper.delete_from_table("todos", where_filters=test_records)
                wrapper.logger.info("Batch test cleanup completed successfully")
        except Exception as cleanup_error:
            wrapper.logger.error(f"Error during batch test cleanup: {cleanup_error}")


@pytest.mark.asyncio
async def test_complex_queries(supabase_wrapper: SupabaseService) -> None:
    """Test complex query operations including filtering, ordering, and pagination."""
    wrapper = supabase_wrapper
    test_records = []

    try:
        wrapper.logger.info("Starting complex queries test")

        # Setup test data with valid status values
        test_todos = [
            {
                "name": "Complex Test 1",
                "email": "complex1@test.com",
                "status": "pending",
                "priority": 1,
                "tags": ["test", "complex", "first"],
                "is_active": True,
            },
            {
                "name": "Complex Test 2",
                "email": "complex2@test.com",
                "status": "completed",
                "priority": 2,
                "tags": ["test", "complex", "second"],
                "is_active": True,
            },
            {
                "name": "Complex Test 3",
                "email": "complex3@test.com",
                "status": "archived",
                "priority": 3,
                "tags": ["test", "complex", "third"],
                "is_active": False,
            },
        ]

        # Insert test records
        for todo in test_todos:
            insert_result = await wrapper.insert_into_table("todos", todo)
            assert (
                insert_result.records[0]["name"] == todo["name"]
            ), "Record should be inserted correctly"
            test_records.append(("email", "like", "%complex%@test.com"))

        # Test 1: Complex filtering
        wrapper.logger.info("Test 1: Testing complex filtering")
        filter_result = await wrapper.select_from_table(
            "todos",
            fields=["*"],
            where_filters=[
                ("status", "in", ["pending", "completed"]),
                ("is_active", "eq", True),
                ("priority", "lte", 2),
                ("email", "like", "%complex%@test.com"),
            ],
        )

        # Validate specific records are found
        found_names = {record["name"] for record in filter_result}
        expected_names = {"Complex Test 1", "Complex Test 2"}
        assert found_names == expected_names, "Should find exactly Complex Test 1 and 2"

        # Test 2: Ordering
        wrapper.logger.info("Test 2: Testing ordering")
        ordered_result = await wrapper.select_from_table(
            "todos",
            fields=["*"],
            where_filters=[("name", "like", "%Complex Test%")],
            order_by={"priority": "desc"},
        )

        # Validate correct ordering
        priorities = [record["priority"] for record in ordered_result]
        assert priorities == [
            3,
            2,
            1,
        ], "Records should be ordered by priority descending"

        # Test 3: Pagination
        wrapper.logger.info("Test 3: Testing pagination")
        page_size = 2
        page_1 = await wrapper.select_from_table(
            "todos",
            fields=["*"],
            where_filters=[("name", "like", "%Complex Test%")],
            order_by={"priority": "asc"},
            limit=page_size,
            offset=(1 - 1) * page_size,
        )

        # Validate pagination content
        page_1_names = [record["name"] for record in page_1]
        assert page_1_names == [
            "Complex Test 1",
            "Complex Test 2",
        ], "First page should contain first two records by priority"

        # Test 4: Combined operations
        wrapper.logger.info("Test 4: Testing combined operations")
        combined_result = await wrapper.select_from_table(
            "todos",
            fields=["*"],
            where_filters=[("is_active", "eq", True), ("priority", "gt", 1)],
            order_by={"priority": "desc"},
            limit=1,
            offset=0,
        )

        # Validate specific record properties
        assert (
            combined_result[0]["name"] == "Complex Test 2"
        ), "Should find Complex Test 2"
        assert combined_result[0]["priority"] == 2, "Should have priority 2"
        assert combined_result[0]["is_active"] is True, "Should be active"

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
async def test_domain_management(supabase_wrapper: SupabaseService) -> None:
    """Test domain management operations."""
    wrapper = supabase_wrapper

    try:
        # Test valid domain setting
        domains = await wrapper.select_from_table(
            "domains",
            ["id", "name"],
            where_filters=[("name", "eq", "Dynamic Healing Group")],
        )
        assert domains is not None, "Should find test domain"

        domain_id = domains[0]["id"]
        # Set the domain
        await wrapper.set_current_domain(domain_id)

        # Verify domain setting by attempting to access domain-specific data
        domain_data = await wrapper.select_from_table(
            "domains", ["id", "name"], where_filters=[("id", "eq", domain_id)]
        )
        assert domain_data is not None, "Should be able to access domain data"
        assert domain_data[0]["id"] == domain_id, "Should access correct domain"

        # Test invalid domain
        with pytest.raises(SupabaseAuthorizationError):
            await wrapper.set_current_domain("invalid_domain_id")

        # Test domain clearing
        await wrapper.set_current_domain(None)
        # Verify clearing by checking we can still access general data
        general_data = await wrapper.select_from_table("domains", ["id", "name"])
        assert (
            general_data is not None
        ), "Should be able to access general data after clearing domain"

    except Exception as e:
        wrapper.logger.error(f"Domain management test failed: {str(e)}")
        raise


@pytest.mark.asyncio
async def test_connection_handling():
    """Test connection handling with valid and invalid credentials."""
    load_dotenv()
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

    # Test valid connection
    service = SupabaseService(url, key)
    # Verify connection by making a simple query
    try:
        result = await service.select_from_table("domains", ["id"], limit=1)
        assert result is not None, "Should be able to query with valid connection"
    except Exception as e:
        pytest.fail(f"Valid connection failed: {str(e)}")

    # Test invalid connection
    with pytest.raises(SupabaseConnectionError):
        SupabaseService("invalid_url", "invalid_key")


@pytest.mark.asyncio
async def test_authentication_flow():
    """Test authentication flow with valid and invalid credentials."""
    load_dotenv()
    email = os.getenv("TEST_EMAIL")
    password = os.getenv("TEST_PASSWORD")

    # Test valid authentication
    service = SupabaseService(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
    await service.login(email, password)
    user = await service.get_user()
    assert user is not None, "Should get valid user after login"
    assert user.email == email, "User email should match login email"

    # Test invalid authentication
    service_invalid = SupabaseService(
        os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY")
    )
    with pytest.raises(SupabaseAuthenticationError):
        await service_invalid.login("invalid@email.com", "wrongpassword")


@pytest.mark.asyncio
async def test_crud_error_handling(supabase_wrapper: SupabaseService) -> None:
    """Test error handling for CRUD operations."""
    wrapper = supabase_wrapper
    test_records = []  # Track any test records that might be created

    try:
        wrapper.logger.info("Starting CRUD error handling tests")

        # Initial cleanup to ensure a clean state
        wrapper.logger.info("Performing initial cleanup...")
        try:
            await wrapper.delete_from_table(
                "todos", where_filters=[("name", "like", "%test%")]
            )
            wrapper.logger.info("Initial cleanup completed successfully")
        except Exception as e:
            wrapper.logger.error(f"Error during initial cleanup: {str(e)}")

        # Test 1: Invalid table name
        wrapper.logger.info("Test 1: Testing invalid table name")
        with pytest.raises(SupabaseQueryError) as exc_info:
            await wrapper.select_from_table("nonexistent_table", ["*"])
        error_msg = str(exc_info.value).lower()
        assert "nonexistent_table" in error_msg and "table" in error_msg

        # Test 2: Invalid column name
        wrapper.logger.info("Test 2: Testing invalid column name")
        with pytest.raises(SupabaseQueryError) as exc_info:
            await wrapper.insert_into_table("todos", {"nonexistent_column": "value"})
        error_msg = str(exc_info.value).lower()
        assert "nonexistent_column" in error_msg and "column" in error_msg

        # Test 3: Invalid data type
        wrapper.logger.info("Test 3: Testing invalid data type")
        with pytest.raises(SupabaseQueryError) as exc_info:
            await wrapper.insert_into_table(
                "todos",
                {"priority": "not_a_number"},  # priority should be integer
            )
        error_msg = str(exc_info.value).lower()
        assert "priority" in error_msg or "type" in error_msg

        # Test 4: Violating NOT NULL constraint
        wrapper.logger.info("Test 4: Testing NOT NULL constraint violation")
        with pytest.raises(SupabaseQueryError) as exc_info:
            await wrapper.insert_into_table(
                "todos",
                {"email": None},  # email is required
            )
        error_msg = str(exc_info.value).lower()
        assert "null" in error_msg or "required" in error_msg

        # Test 5: Invalid filter operator
        wrapper.logger.info("Test 5: Testing invalid filter operator")
        with pytest.raises(SupabaseQueryError) as exc_info:
            await wrapper.select_from_table(
                "todos", ["*"], where_filters=[("name", "invalid_operator", "value")]
            )
        error_msg = str(exc_info.value).lower()
        assert "operator" in error_msg or "invalid" in error_msg

        # Test 6: Empty update fields
        wrapper.logger.info("Test 6: Testing empty update fields")
        with pytest.raises(SupabaseQueryError) as exc_info:
            await wrapper.update_table(
                "todos", update_fields={}, where_filters=[("id", "eq", 1)]
            )
        error_msg = str(exc_info.value).lower()
        assert "empty" in error_msg or "invalid" in error_msg

        # Test 7: Delete without filters
        wrapper.logger.info("Test 7: Testing delete without filters")
        with pytest.raises(SupabaseQueryError) as error:
            await wrapper.delete_from_table("todos", [])
        error_msg = str(error.value).lower()
        assert "failed to delete" in error_msg or "delete" in error_msg

        # Test 8: Invalid enum value
        wrapper.logger.info("Test 8: Testing invalid enum value")
        with pytest.raises(SupabaseQueryError) as exc_info:
            await wrapper.insert_into_table(
                "todos",
                {
                    "name": "test",
                    "email": "test@example.com",
                    "status": "invalid_status",
                },
            )
        error_msg = str(exc_info.value).lower()
        assert "status" in error_msg or "invalid" in error_msg

        wrapper.logger.info("All CRUD error handling tests completed successfully")

    except Exception as e:
        wrapper.logger.error(
            f"Unexpected error during CRUD error handling tests: {str(e)}"
        )
        raise

    finally:
        wrapper.logger.info("Cleaning up after CRUD error handling tests...")
        try:
            if test_records:
                await wrapper.delete_from_table("todos", where_filters=test_records)
                wrapper.logger.info("Test cleanup completed successfully")

            # Additional safety cleanup
            await wrapper.delete_from_table(
                "todos", where_filters=[("name", "like", "%test%")]
            )

            await wrapper.cleanup()
            wrapper.logger.info("Service cleanup completed successfully")

        except Exception as e:
            wrapper.logger.error(f"Error during test cleanup: {str(e)}")
        wrapper.logger.info("CRUD error handling tests cleanup finished")
