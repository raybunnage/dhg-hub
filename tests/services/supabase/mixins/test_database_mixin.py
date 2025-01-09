import pytest
from unittest.mock import Mock, AsyncMock
from src.services.supabase.mixins.database_mixin import DatabaseMixin
from src.core.exceptions import SupabaseQueryError


class TestDatabaseMixin:
    @pytest.fixture
    def db_mixin(self):
        """Create DatabaseMixin instance with mocked supabase client."""
        mixin = DatabaseMixin()
        mixin.supabase = Mock()
        mixin._logger = Mock()
        return mixin

    @pytest.mark.asyncio
    async def test_select_from_table_basic(self, db_mixin):
        """Test basic select operation."""
        # Setup
        table_name = "users"
        fields = ["id", "name"]
        where_filters = [("age", "gt", 18)]
        mock_response = [{"id": 1, "name": "Test User"}]

        # Mock the query builder chain
        query_chain = Mock()
        db_mixin.supabase.from_.return_value = query_chain
        query_chain.select.return_value = query_chain
        query_chain.gt.return_value = query_chain
        query_chain.execute = AsyncMock(return_value=Mock(data=mock_response))

        # Execute
        result = await db_mixin.select_from_table_basic(
            table_name, fields, where_filters
        )

        # Assert
        assert result == mock_response
        db_mixin.supabase.from_.assert_called_once_with(table_name)
        query_chain.select.assert_called_once_with(",".join(fields))

    @pytest.mark.asyncio
    async def test_validate_select_against_constraints(self, db_mixin):
        """Test field validation against table constraints."""
        # Setup
        table_name = "users"
        fields = {"id": 1, "invalid_field": "test"}
        constraints = {"not_null": ["id", "name"], "nullable": ["email"], "check": []}

        # Mock get_table_constraints
        db_mixin.get_table_constraints = AsyncMock(return_value=constraints)

        # Execute & Assert
        with pytest.raises(SupabaseQueryError, match="Invalid fields"):
            await db_mixin.validate_select_against_constraints(table_name, fields)

    # Add more database tests...
