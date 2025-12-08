# Application Configuration

from typing import List
from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Project Info
    PROJECT_NAME: str = "Netta's Bounce Around Daycare Management System"
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # OpenAI
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4"  # Can switch to gpt-3.5-turbo for cost savings
    
    # SendGrid Email
    SENDGRID_API_KEY: str
    SENDGRID_FROM_EMAIL: str = "noreply@nettasbounce.com"
    SENDGRID_FROM_NAME: str = "Netta's Bounce Around Daycare"
    
    # Twilio SMS (Optional but recommended for emergency alerts)
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_PHONE_NUMBER: str = ""
    
    # AWS S3 for file storage
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_S3_BUCKET: str = "nettas-daycare-files"
    AWS_REGION: str = "us-east-1"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # Alternative
        "http://localhost:8000",  # Backend
    ]
    
    # Daycare-specific settings
    DAYCARE_NAME: str = "Netta's Bounce Around Daycare LLC"
    DAYCARE_ADDRESS: str = "Chicago, IL"
    DAYCARE_PHONE: str = ""
    DAYCARE_EMAIL: str = ""
    OPERATING_HOURS_MORNING: str = "6:00 AM - 6:00 PM"
    OPERATING_HOURS_EVENING: str = "6:00 PM - 12:00 AM"
    MAX_CHILDREN_ENROLLMENT: int = 20
    CURRENT_ENROLLMENT: int = 15
    AGE_RANGE_MIN: str = "6 weeks"
    AGE_RANGE_MAX: str = "12 years"
    
    # Compliance
    LATE_PICKUP_GRACE_MINUTES: int = 15  # Grace period before late fee
    LATE_PICKUP_FEE_PER_MINUTE: float = 1.00  # $1 per minute after grace
    VACCINE_GRACE_PERIOD_DAYS: int = 30  # New enrollment grace period
    DCFS_LICENSE_NUMBER: str = ""
    
    # File Upload
    MAX_UPLOAD_SIZE_MB: int = 10
    ALLOWED_FILE_EXTENSIONS: List[str] = [".pdf", ".jpg", ".jpeg", ".png", ".doc", ".docx"]
    
    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str]:
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()