from typing import List, Dict, Any
from services.core.base_logging import log_method
from ...core.exceptions import (
    SupabaseStorageError,
    SupabaseStorageAuthError,
    map_storage_error,
)
from postgrest import StorageApiError


class StorageMixin:
    """Mixin for storage operations."""

    @log_method()
    async def upload_file(
        self, bucket: str, file_path: str, file_data: bytes, content_type: str = None
    ) -> str:
        """Upload a file to Supabase Storage.

        Args:
            bucket: Storage bucket name
            file_path: Path where file will be stored
            file_data: Binary file data
            content_type: MIME type of the file

        Returns:
            str: Public URL of the uploaded file

        Raises:
            ValueError: If invalid parameters are provided
            SupabaseStorageAuthError: If storage authentication fails
            SupabaseStoragePermissionError: If insufficient permissions
            SupabaseStorageQuotaError: If storage quota is exceeded
            SupabaseStorageValidationError: If file validation fails
            SupabaseStorageError: For other storage-related errors
        """
        if not bucket or not isinstance(bucket, str):
            raise ValueError("Bucket must be a non-empty string")
        if not file_data:
            raise ValueError("File data cannot be empty")
        if not file_path or not isinstance(file_path, str):
            raise ValueError("File path must be a non-empty string")

        try:
            response = await self.supabase.storage.from_(bucket).upload(
                file_path,
                file_data,
                {"content-type": content_type} if content_type else None,
            )
            if not response or "Key" not in response:
                raise SupabaseStorageError("Invalid response from storage upload")
            return response["Key"]
        except StorageApiError as e:
            raise map_storage_error(e)
        except Exception as e:
            raise SupabaseStorageError("Failed to upload file", original_error=e)

    @log_method()
    async def download_file(self, bucket: str, file_path: str) -> bytes:
        """Download a file from Supabase Storage.

        Args:
            bucket: Storage bucket name
            file_path: Path to the file

        Returns:
            bytes: File data

        Raises:
            ValueError: If invalid parameters are provided
            SupabaseStorageAuthError: If storage authentication fails
            SupabaseStoragePermissionError: If insufficient permissions
            SupabaseStorageNotFoundError: If file not found
            SupabaseStorageError: For other storage-related errors
        """
        if not bucket or not isinstance(bucket, str):
            raise ValueError("Bucket must be a non-empty string")
        if not file_path or not isinstance(file_path, str):
            raise ValueError("File path must be a non-empty string")

        try:
            response = await self.supabase.storage.from_(bucket).download(file_path)
            if not response:
                raise SupabaseStorageError("No data received from storage download")
            return response
        except StorageApiError as e:
            raise map_storage_error(e)
        except Exception as e:
            raise SupabaseStorageError("Failed to download file", original_error=e)

    @log_method()
    async def delete_file(self, bucket: str, file_paths: list[str]) -> bool:
        """Delete files from Supabase Storage.

        Args:
            bucket: Storage bucket name
            file_paths: List of file paths to delete

        Returns:
            bool: True if deletion was successful

        Raises:
            ValueError: If invalid parameters are provided
            SupabaseStorageAuthError: If storage authentication fails
            SupabaseStoragePermissionError: If insufficient permissions
            SupabaseStorageNotFoundError: If any file not found
            SupabaseStorageError: For other storage-related errors
        """
        if not bucket or not isinstance(bucket, str):
            raise ValueError("Bucket must be a non-empty string")
        if not file_paths or not isinstance(file_paths, list):
            raise ValueError("File paths must be a non-empty list")
        if not all(isinstance(path, str) for path in file_paths):
            raise ValueError("All file paths must be strings")

        try:
            await self.supabase.storage.from_(bucket).remove(file_paths)
            return True
        except StorageApiError as e:
            raise map_storage_error(e)
        except Exception as e:
            raise SupabaseStorageError("Failed to delete files", original_error=e)

    @log_method()
    async def list_files(self, bucket: str, path: str = "") -> list[dict]:
        """List files in a storage bucket.

        Args:
            bucket: Storage bucket name
            path: Optional path prefix to filter by

        Returns:
            list[dict]: List of file metadata

        Raises:
            ValueError: If invalid parameters are provided
            SupabaseStorageAuthError: If storage authentication fails
            SupabaseStoragePermissionError: If insufficient permissions
            SupabaseStorageNotFoundError: If bucket not found
            SupabaseStorageError: For other storage-related errors
        """
        if not bucket or not isinstance(bucket, str):
            raise ValueError("Bucket must be a non-empty string")
        if not isinstance(path, str):
            raise ValueError("Path must be a string")

        try:
            response = await self.supabase.storage.from_(bucket).list(path)
            if response is None:
                return []
            return response
        except StorageApiError as e:
            raise map_storage_error(e)
        except Exception as e:
            raise SupabaseStorageError("Failed to list files", original_error=e)

    @log_method()
    async def create_bucket(self, bucket_name: str, is_public: bool = False) -> dict:
        """Create a new storage bucket.

        Args:
            bucket_name: Name of the bucket to create
            is_public: Whether the bucket should be public

        Returns:
            dict: Created bucket information

        Raises:
            ValueError: If invalid parameters are provided
            SupabaseStorageAuthError: If storage authentication fails
            SupabaseStoragePermissionError: If insufficient permissions
            SupabaseStorageValidationError: If bucket name is invalid
            SupabaseStorageError: For other storage-related errors
        """
        if not bucket_name or not isinstance(bucket_name, str):
            raise ValueError("Bucket name must be a non-empty string")
        if not isinstance(is_public, bool):
            raise ValueError("is_public must be a boolean")

        try:
            response = await self.supabase.storage.create_bucket(
                bucket_name, {"public": is_public}
            )
            if not response:
                raise SupabaseStorageError("Invalid response from bucket creation")
            return response
        except StorageApiError as e:
            raise map_storage_error(e)
        except Exception as e:
            raise SupabaseStorageError("Failed to create bucket", original_error=e)

    @log_method()
    async def get_bucket(self, bucket_name: str) -> dict:
        """Get bucket information.

        Args:
            bucket_name: Name of the bucket

        Returns:
            dict: Bucket information
        """
        try:
            return await self.supabase.storage.get_bucket(bucket_name)
        except Exception as e:
            raise SupabaseStorageError("Failed to get bucket", original_error=e)

    @log_method()
    async def list_buckets(self) -> list[dict]:
        """List all storage buckets.

        Returns:
            list[dict]: List of bucket information
        """
        try:
            return await self.supabase.storage.list_buckets()
        except Exception as e:
            raise SupabaseStorageError("Failed to list buckets", original_error=e)

    @log_method()
    async def delete_bucket(self, bucket_name: str) -> bool:
        """Delete a storage bucket.

        Args:
            bucket_name: Name of the bucket to delete

        Returns:
            bool: True if deletion was successful

        Raises:
            ValueError: If invalid parameters are provided
            SupabaseStorageAuthError: If storage authentication fails
            SupabaseStoragePermissionError: If insufficient permissions
            SupabaseStorageNotFoundError: If bucket not found
            SupabaseStorageError: For other storage-related errors
        """
        if not bucket_name or not isinstance(bucket_name, str):
            raise ValueError("Bucket name must be a non-empty string")

        try:
            await self.supabase.storage.delete_bucket(bucket_name)
            return True
        except StorageApiError as e:
            raise map_storage_error(e)
        except Exception as e:
            raise SupabaseStorageError("Failed to delete bucket", original_error=e)

    @log_method()
    async def empty_bucket(self, bucket_name: str) -> bool:
        """Empty a storage bucket.

        Args:
            bucket_name: Name of the bucket to empty

        Returns:
            bool: True if operation was successful

        Raises:
            ValueError: If invalid parameters are provided
            SupabaseStorageAuthError: If storage authentication fails
            SupabaseStoragePermissionError: If insufficient permissions
            SupabaseStorageNotFoundError: If bucket not found
            SupabaseStorageError: For other storage-related errors
        """
        if not bucket_name or not isinstance(bucket_name, str):
            raise ValueError("Bucket name must be a non-empty string")

        try:
            await self.supabase.storage.empty_bucket(bucket_name)
            return True
        except StorageApiError as e:
            raise map_storage_error(e)
        except Exception as e:
            raise SupabaseStorageError("Failed to empty bucket", original_error=e)
