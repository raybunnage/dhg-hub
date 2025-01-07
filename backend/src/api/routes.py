from fastapi import APIRouter

router = APIRouter()


@router.get('/health')
async def health_check() -> dict[str, str]:
    """Check the health status of the API.

    Returns:
        dict: A dictionary containing the health status
    """
    return {'status': 'healthy'}
