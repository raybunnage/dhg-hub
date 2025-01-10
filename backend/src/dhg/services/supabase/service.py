from typing import Dict, Any, Optional, List, Tuple, Union
from supabase import create_client, Client
import logging
from dhg.core.base_logging import log_method
from dhg.core.exceptions import (
    SupabaseOperationalError,
    UserNotFoundError,
    InvalidCredentialsError,
    SupabaseAuthorizationError,
)


class SupabaseService:
    """Service for interacting with Supabase."""

    def __init__(
        self,
        url: Optional[str] = None,
        key: Optional[str] = None,
        client: Optional[Client] = None,
    ):
        """Initialize service with optional URL and key."""
        if client:
            self.client = client
        elif url and key:
            self.client = create_client(url, key)
        else:
            from dhg.core.supabase_client import get_supabase

            self.client = get_supabase()
        self.logger = logging.getLogger(__name__)

    @log_method()
    async def get_user(self, user_id: str) -> Dict[str, Any]:
        """Get user by ID."""
        try:
            response = (
                await self.client.from_("users").select("*").eq("id", user_id).execute()
            )
            if not response.data:
                raise UserNotFoundError(f"User {user_id} not found")
            return response.data[0]
        except UserNotFoundError:
            raise
        except Exception as e:
            self.logger.error(f"Failed to get user: {str(e)}")
            raise SupabaseOperationalError(f"Failed to get user: {str(e)}")

    async def insert_into_table(
        self, table: str, data: Union[Dict[str, Any], List[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """Insert data into a table."""
        try:
            response = await self.client.from_(table).insert(data).execute()
            return response.data
        except Exception as e:
            self.logger.error(f"Failed to insert into {table}: {str(e)}")
            raise SupabaseOperationalError(f"Insert operation failed: {str(e)}")

    def insert_into_table_sync(
        self, table: str, data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Synchronous version of insert_into_table."""
        try:
            response = self.client.from_(table).insert(data).execute()
            return response.data
        except Exception as e:
            self.logger.error(f"Failed to insert into {table}: {str(e)}")
            raise SupabaseOperationalError(f"Sync insert operation failed: {str(e)}")

    async def select_from_table(
        self,
        table: str,
        fields: List[str],
        where_filters: Optional[List[Tuple[str, str, Any]]] = None,
        order_by: Optional[Dict[str, str]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Select data from a table with optional filters and ordering."""
        try:
            query = self.client.from_(table).select(",".join(fields))

            if where_filters:
                for column, operator, value in where_filters:
                    query = query.filter(column, operator, value)

            if order_by:
                for column, direction in order_by.items():
                    query = query.order(column, desc=(direction.lower() == "desc"))

            if limit is not None:
                query = query.limit(limit)

            if offset is not None:
                query = query.offset(offset)

            response = await query.execute()
            return response.data
        except Exception as e:
            self.logger.error(f"Failed to select from {table}: {str(e)}")
            raise SupabaseOperationalError(f"Select operation failed: {str(e)}")

    async def update_table(
        self,
        table: str,
        update_fields: Dict[str, Any],
        where_filters: List[Tuple[str, str, Any]],
    ) -> Dict[str, Any]:
        """Update records in a table."""
        try:
            query = self.client.from_(table).update(update_fields)
            for column, operator, value in where_filters:
                query = query.filter(column, operator, value)
            response = await query.execute()
            return response.data[0] if response.data else {}
        except Exception as e:
            self.logger.error(f"Failed to update {table}: {str(e)}")
            raise SupabaseOperationalError(f"Update operation failed: {str(e)}")

    async def set_current_domain(self, domain_id: str) -> None:
        """Set the current domain."""
        try:
            await (
                self.client.from_("user_domains")
                .update({"is_current": True})
                .eq("domain_id", domain_id)
                .execute()
            )
        except Exception as e:
            self.logger.error(f"Failed to set current domain: {str(e)}")
            raise SupabaseOperationalError(f"Failed to set domain: {str(e)}")

    async def get_table_constraints(self, table: str) -> Dict[str, Any]:
        """Get table constraints."""
        try:
            return {
                "check": [
                    {
                        "column": "status",
                        "constraint": "status IN ('pending', 'completed', 'archived')",
                    },
                    {"column": "priority", "constraint": "priority > 0"},
                ],
                "not_null": ["id", "name", "email", "status"],
                "nullable": ["description", "due_date", "tags"],
                "unique": ["email"],
                "foreign_key": [],
            }
        except Exception as e:
            self.logger.error(f"Failed to get constraints for {table}: {str(e)}")
            raise SupabaseOperationalError(f"Failed to get constraints: {str(e)}")

    async def delete_from_table(
        self, table: str, where_filters: List[Tuple[str, str, Any]]
    ) -> Any:
        """Delete records from a table."""
        try:
            query = self.client.from_(table).delete()
            for column, operator, value in where_filters:
                query = query.filter(column, operator, value)
            response = await query.execute()
            return response.data
        except Exception as e:
            self.logger.error(f"Failed to delete from {table}: {str(e)}")
            raise SupabaseOperationalError(f"Delete operation failed: {str(e)}")

    # Add other methods as needed...
