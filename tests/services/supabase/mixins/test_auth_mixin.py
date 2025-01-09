import pytest
from unittest.mock import Mock, patch, AsyncMock
from gotrue.errors import AuthApiError

from src.services.supabase.mixins.auth_mixin import AuthMixin
from src.core.exceptions import SupabaseAuthenticationError


class TestAuthMixin:
    @pytest.fixture
    def auth_mixin(self):
        """Create AuthMixin instance with mocked supabase client."""
        mixin = AuthMixin()
        mixin.supabase = Mock()
        mixin.supabase.auth = AsyncMock()
        mixin._logger = Mock()
        return mixin

    @pytest.mark.asyncio
    async def test_login_success(self, auth_mixin):
        """Test successful login."""
        # Setup
        email = "test@example.com"
        password = "password123"
        mock_user = {"id": "123", "email": email}
        auth_mixin.supabase.auth.sign_in_with_password.return_value.user = mock_user

        # Execute
        result = await auth_mixin.login(email, password)

        # Assert
        assert result is True
        auth_mixin.supabase.auth.sign_in_with_password.assert_called_once_with(
            {"email": email, "password": password}
        )

    @pytest.mark.asyncio
    async def test_login_missing_credentials(self, auth_mixin):
        """Test login with missing credentials."""
        with pytest.raises(
            SupabaseAuthenticationError, match="Email and password are required"
        ):
            await auth_mixin.login("", "")

    @pytest.mark.asyncio
    async def test_login_auth_api_error(self, auth_mixin):
        """Test login with AuthApiError."""
        auth_mixin.supabase.auth.sign_in_with_password.side_effect = AuthApiError(
            "Invalid credentials"
        )

        with pytest.raises(SupabaseAuthenticationError):
            await auth_mixin.login("test@example.com", "wrong_password")

    # Add more auth tests...
