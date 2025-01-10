from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic_settings import BaseSettings
from fastapi.testclient import TestClient
import jwt

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5175"],  # Vite's default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Replace the get_current_user dependency with Supabase token validation
async def verify_supabase_token(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

    token = auth_header.split(" ")[1]
    try:
        # Verify the JWT token using your Supabase public key
        # You can get this from your Supabase dashboard
        decoded = jwt.decode(
            token,
            settings.SUPABASE_JWT_PUBLIC_KEY,
            algorithms=["HS256"],
            audience="authenticated",
        )
        return decoded
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )


# Example protected route using Supabase auth
@app.get("/protected")
async def protected_route(user_data: dict = Depends(verify_supabase_token)):
    return {"message": "This is protected", "user": user_data}


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
    SUPABASE_JWT_PUBLIC_KEY: str  # Add this for token verification

    class Config:
        env_file = ".env"


settings = Settings()

client = TestClient(app)


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
