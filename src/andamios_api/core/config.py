import os
import logging
from pathlib import Path
from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import Field, validator

class Settings(BaseSettings):
    # Environment
    environment: str = Field(default="development", env="ENVIRONMENT")
    
    # Database
    database_url: str = Field(default="sqlite:///andamios_dev.db", env="DATABASE_URL")
    database_engine: str = Field(default="duckdb", env="DATABASE_ENGINE")
    
    # API Server
    api_host: str = Field(default="localhost", env="API_HOST")
    api_port: int = Field(default=8001, env="API_PORT")
    api_debug: bool = Field(default=True, env="API_DEBUG")
    api_reload: bool = Field(default=True, env="API_RELOAD")
    
    # JWT Authentication
    jwt_secret_key: str = Field(default="dev-secret-key-change-in-production", env="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    jwt_access_token_expire_minutes: int = Field(default=30, env="JWT_ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # CORS
    cors_allow_origins: str = Field(default="http://localhost:3000,http://localhost:8080", env="CORS_ALLOW_ORIGINS")
    cors_allow_credentials: bool = Field(default=True, env="CORS_ALLOW_CREDENTIALS")
    cors_allow_methods: str = Field(default="GET,POST,PUT,DELETE,OPTIONS", env="CORS_ALLOW_METHODS")
    cors_allow_headers: str = Field(default="*", env="CORS_ALLOW_HEADERS")
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s", env="LOG_FORMAT")
    
    @validator('jwt_secret_key')
    def validate_jwt_secret_key(cls, v, values):
        environment = values.get('environment', 'development')
        if environment == 'production' and v in ['dev-secret-key-change-in-production', 'your-production-secret-key-here']:
            raise ValueError('JWT secret key must be changed in production environment')
        return v
    
    @validator('database_url')
    def validate_database_url(cls, v, values):
        if not v or v.strip() == "":
            raise ValueError('Database URL is required')
        return v
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Convert CORS origins string to list"""
        return [origin.strip() for origin in self.cors_allow_origins.split(',') if origin.strip()]
    
    @property
    def cors_methods_list(self) -> List[str]:
        """Convert CORS methods string to list"""
        return [method.strip() for method in self.cors_allow_methods.split(',') if method.strip()]
    
    class Config:
        env_file = ".env"
        case_sensitive = False

def get_settings() -> Settings:
    """Get application settings with environment-specific configuration"""
    
    # Detect environment
    environment = os.getenv("ENVIRONMENT", "development")
    
    # Load environment-specific .env file
    project_root = Path(__file__).parent.parent.parent.parent
    env_file = project_root / f".env.{environment}"
    
    if not env_file.exists():
        # Fallback to generic .env file
        env_file = project_root / ".env"
        if not env_file.exists():
            # No environment file found, use defaults
            env_file = None
    
    # Create settings instance
    if env_file:
        settings = Settings(_env_file=str(env_file))
    else:
        settings = Settings()
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format=settings.log_format
    )
    
    return settings

def validate_required_config(settings: Settings) -> None:
    """Validate that required configuration is present for the current environment"""
    
    errors = []
    
    # Production-specific validations
    if settings.environment == "production":
        if settings.jwt_secret_key in ['dev-secret-key-change-in-production', 'your-production-secret-key-here']:
            errors.append("JWT_SECRET_KEY must be set to a secure value in production")
        
        if settings.api_debug:
            errors.append("API_DEBUG should be false in production")
        
        if "localhost" in settings.cors_allow_origins:
            errors.append("CORS_ALLOW_ORIGINS should not include localhost in production")
    
    # General validations
    if not settings.database_url or settings.database_url.strip() == "":
        errors.append("DATABASE_URL is required")
    
    if not settings.jwt_secret_key or len(settings.jwt_secret_key) < 16:
        errors.append("JWT_SECRET_KEY must be at least 16 characters long")
    
    if errors:
        error_message = f"Configuration validation failed for environment '{settings.environment}':\n"
        for error in errors:
            error_message += f"  - {error}\n"
        raise ValueError(error_message)

# Global settings instance
settings = get_settings()

# Validate configuration on import
validate_required_config(settings)