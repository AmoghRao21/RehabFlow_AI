"""
Centralized configuration management for RehabFlow AI.
Loads environment variables and provides application-wide settings.
"""
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Application configuration class."""
    
    # Base paths
    BASE_DIR: Path = Path(__file__).parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    ASSETS_DIR: Path = BASE_DIR / "assets"
    
    # Database configuration
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        f"sqlite:///{DATA_DIR}/rehabflow.db"
    )
    
    # AI Model configuration
    MEDGEMMA_MODEL_NAME: str = os.getenv(
        "MEDGEMMA_MODEL_NAME", 
        "google/medgemma-2b"
    )
    MEDGEMMA_DEVICE: str = os.getenv("MEDGEMMA_DEVICE", "cpu")
    MEDGEMMA_MAX_LENGTH: int = int(os.getenv("MEDGEMMA_MAX_LENGTH", "512"))
    
    # Gradio configuration
    GRADIO_SERVER_NAME: str = os.getenv("GRADIO_SERVER_NAME", "127.0.0.1")
    GRADIO_SERVER_PORT: int = int(os.getenv("GRADIO_SERVER_PORT", "7860"))
    GRADIO_SHARE: bool = os.getenv("GRADIO_SHARE", "False").lower() == "true"
    
    # Concurrency settings
    MAX_WORKERS: int = int(os.getenv("MAX_WORKERS", "4"))
    
    # Security settings
    ENABLE_SANITIZATION: bool = os.getenv("ENABLE_SANITIZATION", "True").lower() == "true"
    ENABLE_VALIDATION: bool = os.getenv("ENABLE_VALIDATION", "True").lower() == "true"
    
    # Logging configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = os.getenv(
        "LOG_FORMAT",
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    @classmethod
    def ensure_directories(cls) -> None:
        """Ensure all required directories exist."""
        cls.DATA_DIR.mkdir(parents=True, exist_ok=True)
        cls.ASSETS_DIR.mkdir(parents=True, exist_ok=True)
        (cls.ASSETS_DIR / "exercises").mkdir(parents=True, exist_ok=True)
        (cls.ASSETS_DIR / "icons").mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def validate(cls) -> bool:
        """Validate configuration settings."""
        try:
            assert cls.MAX_WORKERS > 0, "MAX_WORKERS must be positive"
            assert cls.GRADIO_SERVER_PORT > 0, "GRADIO_SERVER_PORT must be positive"
            assert cls.MEDGEMMA_MAX_LENGTH > 0, "MEDGEMMA_MAX_LENGTH must be positive"
            return True
        except AssertionError as e:
            raise ValueError(f"Configuration validation failed: {e}")


# Initialize directories on module import
Config.ensure_directories()
