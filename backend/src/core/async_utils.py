"""Utilities for async/sync conversion."""

import asyncio
from functools import wraps
from concurrent.futures import ThreadPoolExecutor


def make_sync(async_func):
    """Decorator to convert async methods to sync methods.

    Args:
        async_func: The async function to convert

    Returns:
        A synchronous version of the async function

    Example:
        @make_sync
        async def my_async_func():
            await some_async_operation()
    """

    @wraps(async_func)
    def sync_wrapper(*args, **kwargs):
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            # If no event loop exists, create a new one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        if loop.is_running():
            # If we're in a running event loop, use a thread
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(
                    lambda: asyncio.run(async_func(*args, **kwargs))
                )
                return future.result()
        else:
            # If no loop is running, we can just run it directly
            return loop.run_until_complete(async_func(*args, **kwargs))

    return sync_wrapper
