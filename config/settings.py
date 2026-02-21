"""
Application configuration and settings.
"""

import os
from typing import List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings:
    """Application settings."""

    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = ENVIRONMENT == "development"

    # API
    API_TITLE: str = "Restaurant ML Service API"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "ML predictions for restaurant management system"
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", 8000))
    API_WORKERS: int = int(os.getenv("API_WORKERS", 4))

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://user:password@localhost:5432/rms_db"
    )
    DATABASE_POOL_SIZE: int = int(os.getenv("DATABASE_POOL_SIZE", 10))
    DATABASE_MAX_OVERFLOW: int = int(os.getenv("DATABASE_MAX_OVERFLOW", 20))

    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    REDIS_CACHE_TTL: int = int(os.getenv("REDIS_CACHE_TTL", 3600))

    # Models
    MODEL_BASE_DIR: str = os.getenv("MODEL_BASE_DIR", "models")
    MODEL_CACHE_SIZE: int = int(os.getenv("MODEL_CACHE_SIZE", 5))

    # Security
    API_KEYS: List[str] = os.getenv("API_KEYS", "").split(",")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"

    # CORS
    CORS_ORIGINS: List[str] = os.getenv("CORS_ORIGINS", "*").split(",")
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]

    # Rate Limiting
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = int(
        os.getenv("RATE_LIMIT_REQUESTS_PER_MINUTE", 1000)
    )

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "logs/app.log")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Training
    TRAINING_DAYS_BACK: int = int(os.getenv("TRAINING_DAYS_BACK", 180))
    TRAINING_TEST_SIZE: float = float(os.getenv("TRAINING_TEST_SIZE", 0.2))
    TRAINING_SCHEDULE: str = os.getenv("TRAINING_SCHEDULE", "0 2 * * *")  # 2 AM daily

    # Feature Engineering
    FEATURE_SCALING_ENABLED: bool = os.getenv("FEATURE_SCALING_ENABLED", "true").lower() == "true"
    FEATURE_CACHE_ENABLED: bool = os.getenv("FEATURE_CACHE_ENABLED", "true").lower() == "true"

    # Monitoring
    MONITORING_ENABLED: bool = os.getenv("MONITORING_ENABLED", "true").lower() == "true"
    PROMETHEUS_PORT: int = int(os.getenv("PROMETHEUS_PORT", 8001))

    # Sentry (Error Tracking)
    SENTRY_DSN: str = os.getenv("SENTRY_DSN", "")
    SENTRY_ENABLED: bool = bool(SENTRY_DSN)

    @classmethod
    def validate(cls):
        """Validate critical settings."""
        if not cls.API_KEYS or cls.API_KEYS == [""]:
            raise ValueError("API_KEYS not configured")

        if not cls.DATABASE_URL:
            raise ValueError("DATABASE_URL not configured")

        return True


# Create settings instance
settings = Settings()
