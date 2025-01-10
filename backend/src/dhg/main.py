from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dhg.api.routes import router
from .core.middleware import error_handler
from .core.logging import setup_logging
from .core.config import get_settings
from flask import Flask

# Initialize settings and logging
settings = get_settings()
setup_logging({"log_level": "INFO"})


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting up...")
    yield
    # Shutdown
    print("Shutting down...")


app = FastAPI(title="DHG Hub API", lifespan=lifespan)

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


def create_app():
    app = Flask(__name__)
    # ... configure app ...
    return app
