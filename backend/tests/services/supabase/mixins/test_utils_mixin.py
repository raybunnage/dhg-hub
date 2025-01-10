import pytest
import logging
from unittest.mock import Mock, AsyncMock
from dhg.services.supabase.mixins.utils_mixin import UtilsMixin
from dhg.core.base_logging import CustomLogger


class TestUtilsMixin:
    @pytest.fixture
    def utils_mixin(self):
        """Create a UtilsMixin instance with mocked supabase client."""
        # Configure logging
        logging.basicConfig(level=logging.DEBUG)

        class TestMixin(UtilsMixin):
            def __init__(self):
                self._logger = CustomLogger(self.__class__.__name__)
                self.supabase = Mock()

        return TestMixin()

    @pytest.mark.asyncio
    async def test_get_table_info(self, utils_mixin):
        """Test get_table_info method."""
        # Setup mock response
        mock_response = Mock()
        mock_response.data = {"columns": ["id", "name"]}

        # Setup mock chain
        mock_execute = AsyncMock(return_value=mock_response)
        mock_rpc = Mock()
        mock_rpc.execute = mock_execute

        utils_mixin.supabase.rpc = Mock(return_value=mock_rpc)

        # Execute test
        result = await utils_mixin.get_table_info("test_table")

        # Assert results
        assert result == {"columns": ["id", "name"]}
        utils_mixin.supabase.rpc.assert_called_once_with(
            "get_table_info", {"table_name": "test_table"}
        )
