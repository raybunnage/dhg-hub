import pytest
from unittest.mock import Mock, AsyncMock
from src.services.supabase.mixins.utils_mixin import UtilsMixin
from src.core.exceptions import SupabaseError


class TestUtilsMixin:
    @pytest.fixture
    def utils_mixin(self):
        """Create UtilsMixin instance with mocked supabase client."""
        mixin = UtilsMixin()
        mixin.supabase = Mock()
        mixin._logger = Mock()
        return mixin

    def test_serialize_data_dict(self, utils_mixin):
        """Test serialization of dictionary data."""
        # Setup
        test_data = {"date": "2024-01-01", "nested": {"key": "value"}}

        # Execute
        result = utils_mixin._serialize_data(test_data)

        # Assert
        assert isinstance(result, dict)
        assert "date" in result
        assert "nested" in result

    @pytest.mark.asyncio
    async def test_rpc_success(self, utils_mixin):
        """Test successful RPC call."""
        # Setup
        function_name = "test_function"
        params = {"param1": "value1"}
        expected_result = {"success": True}

        # Mock the RPC chain
        rpc_chain = Mock()
        utils_mixin.supabase.rpc.return_value = rpc_chain
        rpc_chain.execute = AsyncMock(return_value=Mock(data=expected_result))

        # Execute
        result = await utils_mixin.rpc(function_name, params)

        # Assert
        assert result == expected_result
        utils_mixin.supabase.rpc.assert_called_once_with(function_name, params)

    @pytest.mark.asyncio
    async def test_rpc_error(self, utils_mixin):
        """Test RPC call with error."""
        utils_mixin.supabase.rpc.side_effect = Exception("RPC Error")

        with pytest.raises(SupabaseError, match="RPC call to test_function failed"):
            await utils_mixin.rpc("test_function")

    # Add more utility tests...
