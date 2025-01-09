from asyncio import AsyncClient

from ...core.base_logging import Logger, log_method
from ...core.exceptions import (
    SupabaseConnectionError,
    SupabaseError,
)
from ...core.async_utils import make_sync
from datetime import timedelta
from supabase.lib.client_options import ClientOptions
from gotrue import AsyncMemoryStorage, AsyncGoTrueClient
from .mixins.storage_mixin import StorageMixin
from .mixins.database_mixin import DatabaseMixin
from .mixins.auth_mixin import AuthMixin
from .mixins.utils_mixin import UtilsMixin


class SupabaseService(StorageMixin, DatabaseMixin, AuthMixin, UtilsMixin):
    """Service class for interacting with Supabase.

    Provides methods for database operations, authentication, storage,
    and realtime subscriptions through mixins.

    Attributes:
        url (str): Supabase project URL
        api_key (str): Supabase API key
        logger: Logger instance for this service
    """

    DEFAULT_TIMEOUT = 30  # seconds
    MAX_RETRIES = 3
    CHUNK_SIZE = 1000  # for bulk operations
    STORAGE_UPLOAD_LIMIT = 50 * 1024 * 1024  # 50MB

    def __init__(self, url: str, api_key: str):
        """Initialize the Supabase service with all mixins."""
        if not url or not api_key:
            raise SupabaseError("URL and API key are required")

        self.url = url
        self.api_key = api_key
        self._logger = Logger(self.__class__.__name__)

        # Initialize the Supabase client
        self._init_client()

        # Initialize caching and constraints
        self._constraint_cache = {}
        self._cache_timeout = timedelta(minutes=5)

        # Initialize DatabaseMixin attributes
        self.MAX_BATCH_SIZE = 1000
        self.TIMEOUT_SECONDS = 30
        self.RETRY_ATTEMPTS = 3

        # Initialize StorageMixin attributes
        self.STORAGE_UPLOAD_LIMIT = 50 * 1024 * 1024  # 50MB

        # Validate initialization
        self._validate_initialization()

    def _validate_initialization(self) -> None:
        """Validate that all mixins are properly initialized."""
        if not hasattr(self, "_supabase") or not self._supabase:
            raise SupabaseError("Supabase client not initialized")

        self._logger.debug(f"""
        Service initialization details:
        - Client exists: {bool(self._supabase)}
        - Auth client exists: {bool(self._supabase.auth)}
        - Storage client exists: {bool(self._supabase.storage)}
        - Database access ready: {bool(self._supabase.table)}
        - URL valid: {bool(self.url)}
        - API key valid: {bool(self.api_key)}
        - Batch size set: {bool(hasattr(self, 'MAX_BATCH_SIZE'))}
        - Storage limit set: {bool(hasattr(self, 'STORAGE_UPLOAD_LIMIT'))}
        """)

    @log_method()
    def _init_client(self) -> None:
        """Initialize the Supabase async client."""
        try:
            options = ClientOptions(
                schema="public",
                headers={"x-my-custom-header": "my-app-name"},
                persist_session=True,
                auto_refresh_token=True,
                postgrest_client_timeout=self.DEFAULT_TIMEOUT,
            )

            client = AsyncClient(self.url, self.api_key, options=options)
            if not client:
                raise SupabaseConnectionError("Failed to create AsyncClient")

            storage = AsyncMemoryStorage()
            auth_client = AsyncGoTrueClient(
                url=f"{self.url}/auth/v1",
                headers={"apikey": self.api_key},
                storage=storage,
            )
            client.auth = auth_client
            self._supabase = client

        except Exception as e:
            self._logger.error(f"Failed to initialize Supabase client: {str(e)}")
            raise SupabaseConnectionError(
                "Failed to initialize client", original_error=e
            )

    @property
    def supabase(self) -> AsyncClient:
        """Get the Supabase client instance."""
        if not hasattr(self, "_supabase") or not isinstance(
            self._supabase, AsyncClient
        ):
            self._logger.error("Supabase client not properly initialized")
            raise SupabaseConnectionError("Supabase client not properly initialized")
        return self._supabase

    @property
    def logger(self) -> Logger:
        """Get the logger instance for this service."""
        return self._logger

    async def cleanup(self):
        """Cleanup resources when service is no longer needed."""
        try:
            await self.supabase.auth.sign_out()
        except Exception as e:
            self._logger.error("Error during cleanup", error=e)

    async def _ensure_connected(self):
        """Ensure connection is available before operations."""
        if not await self.check_connection():
            await self._init_client()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.cleanup()

    # Database Mixin Sync Wrappers
    @make_sync
    async def select_from_table_sync(self, *args, **kwargs):
        return await self.select_from_table(*args, **kwargs)

    @make_sync
    async def select_from_table_basic_sync(self, *args, **kwargs):
        return await self.select_from_table_basic(*args, **kwargs)

    @make_sync
    async def select_with_join_sync(self, *args, **kwargs):
        return await self.select_with_join(*args, **kwargs)

    @make_sync
    async def insert_into_table_sync(self, *args, **kwargs):
        return await self.insert_into_table(*args, **kwargs)

    @make_sync
    async def update_table_sync(self, *args, **kwargs):
        return await self.update_table(*args, **kwargs)

    @make_sync
    async def delete_from_table_sync(self, *args, **kwargs):
        return await self.delete_from_table(*args, **kwargs)

    @make_sync
    async def validate_select_against_constraints_sync(self, *args, **kwargs):
        return await self.validate_select_against_constraints(*args, **kwargs)

    @make_sync
    async def create_search_index_sync(self, *args, **kwargs):
        return await self.create_search_index(*args, **kwargs)

    @make_sync
    async def get_user_roles_sync(self, *args, **kwargs):
        return await self.get_user_roles(*args, **kwargs)

    @make_sync
    async def check_permission_sync(self, *args, **kwargs):
        return await self.check_permission(*args, **kwargs)

    @make_sync
    async def subscribe_to_table_sync(self, *args, **kwargs):
        return await self.subscribe_to_table(*args, **kwargs)

    # Auth Mixin Sync Wrappers
    @make_sync
    async def login_sync(self, *args, **kwargs):
        return await self.login(*args, **kwargs)

    @make_sync
    async def logout_sync(self, *args, **kwargs):
        return await self.logout(*args, **kwargs)

    @make_sync
    async def signup_sync(self, *args, **kwargs):
        return await self.signup(*args, **kwargs)

    @make_sync
    async def refresh_session_sync(self, *args, **kwargs):
        return await self.refresh_session(*args, **kwargs)

    @make_sync
    async def get_user_sync(self, *args, **kwargs):
        return await self.get_user(*args, **kwargs)

    @make_sync
    async def update_user_sync(self, *args, **kwargs):
        return await self.update_user(*args, **kwargs)

    @make_sync
    async def update_password_sync(self, *args, **kwargs):
        return await self.update_password(*args, **kwargs)

    @make_sync
    async def verify_otp_sync(self, *args, **kwargs):
        return await self.verify_otp(*args, **kwargs)

    @make_sync
    async def verify_email_sync(self, *args, **kwargs):
        return await self.verify_email(*args, **kwargs)

    @make_sync
    async def set_session_sync(self, *args, **kwargs):
        return await self.set_session(*args, **kwargs)

    @make_sync
    async def login_with_provider_sync(self, *args, **kwargs):
        return await self.login_with_provider(*args, **kwargs)

    # Storage Mixin Sync Wrappers
    @make_sync
    async def upload_file_sync(self, *args, **kwargs):
        return await self.upload_file(*args, **kwargs)

    @make_sync
    async def download_file_sync(self, *args, **kwargs):
        return await self.download_file(*args, **kwargs)

    @make_sync
    async def delete_file_sync(self, *args, **kwargs):
        return await self.delete_file(*args, **kwargs)

    @make_sync
    async def list_files_sync(self, *args, **kwargs):
        return await self.list_files(*args, **kwargs)

    @make_sync
    async def create_bucket_sync(self, *args, **kwargs):
        return await self.create_bucket(*args, **kwargs)

    @make_sync
    async def get_bucket_sync(self, *args, **kwargs):
        return await self.get_bucket(*args, **kwargs)

    @make_sync
    async def list_buckets_sync(self, *args, **kwargs):
        return await self.list_buckets(*args, **kwargs)

    @make_sync
    async def delete_bucket_sync(self, *args, **kwargs):
        return await self.delete_bucket(*args, **kwargs)

    @make_sync
    async def empty_bucket_sync(self, *args, **kwargs):
        return await self.empty_bucket(*args, **kwargs)

    # Utils Mixin Sync Wrappers
    @make_sync
    async def rpc_sync(self, *args, **kwargs):
        return await self.rpc(*args, **kwargs)

    # Service Methods Sync Wrappers
    @make_sync
    async def cleanup_sync(self, *args, **kwargs):
        return await self.cleanup(*args, **kwargs)
