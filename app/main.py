from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from pydantic_settings import BaseSettings
from fastapi.testclient import TestClient

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5175"],  # Vite's default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(token: str = Depends(oauth2_scheme)):
    # Implement JWT validation
    pass


@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "Backend is running"}


@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile = File(...)):
    # Handle PDF upload
    pass


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return {"detail": exc.detail}


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"

    class Config:
        env_file = ".env"


settings = Settings()

client = TestClient(app)


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
