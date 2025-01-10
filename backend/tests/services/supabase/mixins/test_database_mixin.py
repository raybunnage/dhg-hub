import pytest
import logging
from unittest.mock import Mock, AsyncMock, PropertyMock
from dhg.services.supabase.mixins.database_mixin import DatabaseMixin
from dhg.core.exceptions import SupabaseQueryError


class TestDatabaseMixin:
    @pytest.fixture
    def db_mixin(self):
        """Create a DatabaseMixin instance with mocked supabase client."""
        # Configure logging for tests
        logging.basicConfig(level=logging.DEBUG)

        mixin = DatabaseMixin()
        mixin.supabase = Mock()
        return mixin

    @pytest.mark.asyncio
    async def test_select_from_table_basic(self, db_mixin):
        """Test basic select operation."""
        # Setup mock response
        mock_response = Mock()
        mock_response.data = [{"id": 1, "name": "test"}]

        # Create the complete mock chain
        mock_execute = AsyncMock(return_value=mock_response)
        mock_eq = Mock()
        mock_eq.execute = mock_execute

        mock_where = Mock()
        mock_where.eq = Mock(return_value=mock_eq)

        mock_select = Mock()
        mock_select.execute = mock_execute
        mock_select.eq = Mock(return_value=mock_eq)

        mock_from = Mock()
        mock_from.select = Mock(return_value=mock_select)

        # Setup the from_ method
        db_mixin.supabase.from_ = Mock(return_value=mock_from)

        # Execute test
        result = await db_mixin.select_from_table_basic(
            table_name="test_table", fields=["id", "name"]
        )

        # Assert results
        assert result == [{"id": 1, "name": "test"}]

        # Verify method chain
        db_mixin.supabase.from_.assert_called_once_with("test_table")
        mock_from.select.assert_called_once()
        assert mock_execute.called

    @pytest.mark.asyncio
    async def test_validate_select_against_constraints(self, db_mixin):
        """Test validation of select constraints."""
        mock_response = Mock()
        mock_response.data = [
            {"column_name": "id", "is_nullable": "NO"},
            {"column_name": "name", "is_nullable": "YES"},
        ]

        db_mixin.supabase.rpc = Mock()
        db_mixin.supabase.rpc.return_value.execute = AsyncMock(
            return_value=mock_response
        )

        # Test with valid fields
        await db_mixin.validate_select_against_constraints(
            "test_table", {"id": 1, "name": "test"}
        )

        # Verify RPC call
        db_mixin.supabase.rpc.assert_called_with(
            "get_table_info", {"p_table_name": "test_table"}
        )

    # Add more database tests...
