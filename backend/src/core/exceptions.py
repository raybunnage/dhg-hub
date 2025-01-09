from typing import Optional
from storage3.utils import StorageException
from gotrue.errors import (
    AuthApiError,
    AuthError,
    AuthInvalidCredentialsError,
    AuthSessionMissingError,
)
from gotrue import AsyncMemoryStorage, SyncMemoryStorage, AsyncGoTrueClient


# Base Exception for your entire application
class ApplicationError(Exception):
    """Base exception class for all application errors"""

    def __init__(self, message: str, original_error: Exception = None):
        self.message = message
        self.original_error = original_error
        super().__init__(self.message)


# Service-level base exceptions
class ServiceError(ApplicationError):
    """Base exception for all service-related errors"""

    pass


# Database specific exceptions
class DatabaseError(ServiceError):
    """Base exception for all database-related errors"""

    pass


class SupabaseError(Exception):
    """Base exception for Supabase errors"""

    def __init__(self, message: str, original_error: Exception = None):
        self.message = message
        self.original_error = original_error
        super().__init__(self.message)


class SupabaseConnectionError(SupabaseError):
    """Raised when unable to establish a connection to Supabase"""

    pass


# Specific Supabase error types
class SupabaseQueryError(SupabaseError):
    """Raised when a query fails"""

    pass


class SupabaseTimeoutError(SupabaseError):
    """Raised when a Supabase operation times out"""

    pass


# AI Service exceptions
class AIServiceError(ServiceError):
    """Base exception for AI-related services"""

    pass


class AnthropicError(AIServiceError):
    """Specific Anthropic-related errors"""

    pass


# Storage service exceptions
class StorageError(Exception):
    """Base class for storage-related errors"""

    pass


class GoogleDriveError(ServiceError):
    """Specific Google Drive-related errors"""

    pass


# Auth related exceptions
class AuthError(ServiceError):
    """Base exception for authentication/authorization related errors"""

    pass


class SupabaseAuthenticationError(AuthError):
    """Raised when Supabase authentication fails (login, signup, etc.)"""

    pass


class SupabaseAuthorizationError(AuthError):
    """Raised when Supabase authorization/permissions fail (RLS, policies)"""

    pass


# Storage specific exceptions
class SupabaseStorageError(SupabaseError):
    """Base exception for Supabase storage-related errors"""

    pass


class SupabaseStorageAuthError(SupabaseStorageError):
    """Raised when storage operation fails due to authentication"""

    pass


class SupabaseStoragePermissionError(SupabaseStorageError):
    """Raised when storage operation fails due to insufficient permissions"""

    pass


class SupabaseStorageQuotaError(SupabaseStorageError):
    """Raised when storage operation fails due to quota limits"""

    pass


class SupabaseStorageNotFoundError(SupabaseStorageError):
    """Raised when requested storage resource is not found"""

    pass


class SupabaseStorageValidationError(SupabaseStorageError):
    """Raised when storage operation fails due to validation"""

    pass


# Authentication specific exceptions
class SupabaseAuthError(SupabaseError):
    """Base class for authentication errors"""

    pass


class SupabaseAuthenticationError(SupabaseAuthError):
    """Raised when authentication fails (login, signup)"""

    pass


class SupabaseInvalidCredentialsError(SupabaseAuthenticationError):
    """Raised when credentials are invalid"""

    pass


class SupabaseSessionError(SupabaseAuthError):
    """Raised when there are session-related issues"""

    pass


class SupabaseSessionMissingError(SupabaseSessionError):
    """Raised when session is required but missing"""

    pass


class SupabaseTokenRefreshError(SupabaseSessionError):
    """Raised when token refresh fails"""

    pass


class SupabaseAuthorizationError(SupabaseAuthError):
    """Raised when authorization fails (insufficient permissions)"""

    pass


class SupabaseEmailVerificationError(SupabaseAuthError):
    """Raised when email verification fails"""

    pass


class SupabaseMFAError(SupabaseAuthError):
    """Raised when MFA-related operations fail"""

    pass


# Add these new exception classes after the other SupabaseAuth exceptions
class SupabaseStorageClientError(SupabaseAuthError):
    """Raised when there are issues with the storage client initialization or operation"""

    pass


class SupabaseAsyncClientError(SupabaseAuthError):
    """Raised when there are issues with the async client initialization or operation"""

    pass


def map_auth_error(error: AuthApiError) -> SupabaseAuthError:
    """Maps GoTrue auth exceptions to our custom exceptions.

    Args:
        error: Original auth exception from GoTrue client

    Returns:
        Appropriate SupabaseAuthError subclass
    """
    error_message = str(error)

    # Add timeout check near the start of the function
    if "timeout" in error_message.lower() or "timed out" in error_message.lower():
        return SupabaseTimeoutError("Operation timed out", original_error=error)

    # Add these new conditions at the start of the function
    if isinstance(error, (AsyncMemoryStorage, SyncMemoryStorage)):
        return SupabaseStorageClientError(
            "Storage client error occurred", original_error=error
        )
    elif isinstance(error, AsyncGoTrueClient):
        return SupabaseAsyncClientError(
            "Async client error occurred", original_error=error
        )

    if isinstance(error, AuthInvalidCredentialsError):
        return SupabaseInvalidCredentialsError(
            "Invalid credentials", original_error=error
        )
    elif isinstance(error, AuthSessionMissingError):
        return SupabaseSessionMissingError("Session is missing", original_error=error)
    elif "token" in error_message.lower() and "refresh" in error_message.lower():
        return SupabaseTokenRefreshError(
            "Failed to refresh token", original_error=error
        )
    elif "verification" in error_message.lower():
        return SupabaseEmailVerificationError(
            "Email verification failed", original_error=error
        )
    elif "mfa" in error_message.lower():
        return SupabaseMFAError("MFA operation failed", original_error=error)
    elif (
        "permission" in error_message.lower() or "unauthorized" in error_message.lower()
    ):
        return SupabaseAuthorizationError(
            "Insufficient permissions", original_error=error
        )
    else:
        return SupabaseAuthenticationError(
            "Authentication failed", original_error=error
        )


def map_storage_error(error: StorageException) -> SupabaseStorageError:
    """Maps Supabase storage exceptions to our custom exceptions.

    Args:
        error: Original storage exception from Supabase client

    Returns:
        Appropriate SupabaseStorageError subclass
    """
    error_message = str(error)

    # Add timeout check near the start of the function
    if "timeout" in error_message.lower() or "timed out" in error_message.lower():
        return SupabaseTimeoutError("Operation timed out", original_error=error)

    if "authentication" in error_message.lower():
        return SupabaseStorageAuthError(
            "Storage authentication failed", original_error=error
        )
    elif "permission" in error_message.lower():
        return SupabaseStoragePermissionError(
            "Insufficient storage permissions", original_error=error
        )
    elif "quota" in error_message.lower():
        return SupabaseStorageQuotaError("Storage quota exceeded", original_error=error)
    elif "not found" in error_message.lower():
        return SupabaseStorageNotFoundError(
            "Storage resource not found", original_error=error
        )
    elif "validation" in error_message.lower():
        return SupabaseStorageValidationError(
            "Storage validation failed", original_error=error
        )
    else:
        return SupabaseStorageError("Storage operation failed", original_error=error)


# to consider in the futre

# from typing import List
# from dataclasses import dataclass


# @dataclass
# class APIError(Exception):
#     """Base API error."""

#     message: str
#     code: int = 400


# def handle_multiple_errors(errors: List[Exception]) -> None:
#     """Handle multiple errors using exception groups."""
#     if errors:
#         raise ExceptionGroup("Multiple errors occurred", errors)
