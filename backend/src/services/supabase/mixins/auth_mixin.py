from typing import Any, Dict, Optional
from ...core.base_logging import log_method
from ...core.exceptions import (
    SupabaseAuthenticationError,
    SupabaseAuthorizationError,
    map_auth_error,
)
from gotrue.errors import AuthApiError


class AuthMixin:
    """Mixin for authentication-related operations."""

    @log_method()
    async def login(self, email: str, password: str) -> bool:
        """Login with email and password."""
        try:
            if not email or not password:
                raise SupabaseAuthenticationError("Email and password are required")

            response = await self.supabase.auth.sign_in_with_password(
                {"email": email, "password": password}
            )

            if not response.user:
                raise SupabaseAuthenticationError("Login failed - no user returned")

            return True
        except AuthApiError as e:
            raise map_auth_error(e)
        except Exception as e:
            raise SupabaseAuthenticationError("Login failed", original_error=e)

    @log_method()
    async def logout(self) -> bool:
        """Logout the current user."""
        try:
            await self.supabase.auth.sign_out()
            return True
        except AuthApiError as e:
            raise map_auth_error(e)
        except Exception as e:
            raise SupabaseAuthenticationError("Logout failed", original_error=e)

    @log_method()
    async def signup(self, email: str, password: str) -> bool:
        """Sign up a new user."""
        try:
            if not email or not password:
                raise SupabaseAuthenticationError("Email and password are required")

            response = await self.supabase.auth.sign_up(
                {"email": email, "password": password}
            )

            if not response.user:
                raise SupabaseAuthenticationError("Signup failed - no user created")

            return True
        except AuthApiError as e:
            raise map_auth_error(e)
        except Exception as e:
            raise SupabaseAuthenticationError("Signup failed", original_error=e)

    @log_method()
    async def refresh_session(self) -> bool:
        """Refresh the current session."""
        try:
            response = await self.supabase.auth.refresh_session()
            if not response.session:
                raise SupabaseAuthenticationError(
                    "Session refresh failed - no session returned"
                )
            return True
        except AuthApiError as e:
            raise map_auth_error(e)
        except Exception as e:
            raise SupabaseAuthenticationError(
                "Failed to refresh session", original_error=e
            )

    @log_method()
    async def get_user(self):
        """Get the current user."""
        try:
            response = await self.supabase.auth.get_user()
            if not response.user:
                raise SupabaseAuthenticationError("No active session found")
            return response.user
        except AuthApiError as e:
            raise map_auth_error(e)
        except Exception as e:
            raise SupabaseAuthenticationError("Failed to get user", original_error=e)

    @log_method()
    async def update_password(self, new_password: str) -> bool:
        """Update password for the currently logged-in user."""
        try:
            await self.supabase.auth.update_user({"password": new_password})
            return True
        except Exception as e:
            raise SupabaseAuthenticationError(
                "Failed to update password", original_error=e
            )

    @log_method()
    async def verify_otp(self, email: str, token: str) -> bool:
        """Verify one-time password token."""
        try:
            await self.supabase.auth.verify_otp(
                {"email": email, "token": token, "type": "email"}
            )
            return True
        except Exception as e:
            raise SupabaseAuthenticationError("Failed to verify OTP", original_error=e)

    @log_method()
    async def set_session(self, access_token: str, refresh_token: str) -> bool:
        """Manually set the session tokens."""
        try:
            await self.supabase.auth.set_session(access_token, refresh_token)
            return True
        except Exception as e:
            raise SupabaseAuthenticationError("Failed to set session", original_error=e)

    @log_method()
    async def login_with_provider(
        self, provider: str, redirect_url: str = None
    ) -> Dict[str, Any]:
        """Login with OAuth provider (Google, GitHub, etc.)."""
        try:
            response = await self.supabase.auth.sign_in_with_oauth(
                {
                    "provider": provider,
                    "options": {"redirect_to": redirect_url} if redirect_url else None,
                }
            )
            return response
        except Exception as e:
            raise SupabaseAuthenticationError(
                f"Failed to login with {provider}", original_error=e
            )

    @log_method()
    async def update_user(self, user_data: dict) -> Any:
        """Update user data."""
        try:
            response = await self.supabase.auth.update_user(user_data)
            if not response.user:
                raise SupabaseAuthenticationError(
                    "User update failed - no user returned"
                )
            return response.user
        except AuthApiError as e:
            raise map_auth_error(e)
        except Exception as e:
            raise SupabaseAuthenticationError("Failed to update user", original_error=e)
