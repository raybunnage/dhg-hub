from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.routes import router
from .core.middleware import error_handler
from .core.logging import setup_logging
from .core.config import get_settings

# Initialize settings and logging
settings = get_settings()
setup_logging({"log_level": "INFO"})

app = FastAPI(title="DHG Hub API")

# Add middleware
app.middleware("http")(error_handler)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router, prefix=f"/api/{settings.API_VERSION}")


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    pass  # Add any initialization here


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    pass  # Add any cleanup here
