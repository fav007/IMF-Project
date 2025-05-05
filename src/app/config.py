import os
from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Base directory
    BASE_DIR: Path = Path(__file__).resolve().parent.parent

    # Upload directory
    UPLOAD_DIR: str = os.path.join(BASE_DIR, "uploads")
    
    # Allowed file extensions
    ALLOWED_EXTENSIONS: set = {".pdf", ".jpg", ".jpeg"}
    
    # Database URL
    DATABASE_URL: str = "sqlite:///./documents.db"
    
    # API settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Document Management API"
    VERSION: str = "1.0.0"
    
    # Security settings
    SECRET_KEY: str = "your-secret-key-here"  # Change this in production
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    class Config:
        case_sensitive = True
        env_file = ".env"

# Create upload directory if it doesn't exist
os.makedirs(Settings().UPLOAD_DIR, exist_ok=True)

settings = Settings() 