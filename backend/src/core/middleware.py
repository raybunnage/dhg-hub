from fastapi import Request, status
from fastapi.responses import JSONResponse
from typing import Union
from supabase.lib.client_options import APIError


async def error_handler(request: Request, call_next):
    try:
        return await call_next(request)
    except APIError as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content={"error": str(e)}
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "Internal server error"},
        )
