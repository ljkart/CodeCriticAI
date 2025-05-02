"""Application configuration settings.

This module contains all configuration settings for the application, loaded from
environment variables with defaults for development.
"""

import os
from datetime import timedelta
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base directory of the application
BASE_DIR = Path(__file__).parent.absolute()

# General Configuration
DEBUG = os.getenv("FLASK_ENV") == "development"
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")

# AI Service Configuration
AI_API_KEY = os.getenv("AI_API_KEY", "")
AI_MODEL = os.getenv("AI_MODEL", "gpt-3.5-turbo")

# File Upload Configuration
UPLOAD_FOLDER = Path(
    os.getenv("UPLOAD_FOLDER", str(BASE_DIR / "static/uploads"))
)
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload size

# Supported file extensions and their language mappings
ALLOWED_EXTENSIONS = frozenset(
    {
        "py",  # Python
        "js",  # JavaScript
        "jsx",  # React JSX
        "ts",  # TypeScript
        "tsx",  # React TypeScript
    }
)

LANGUAGE_MAPPING = {
    "python": ["py"],
    "javascript": ["js, jsx"],
    "typescript": ["ts", "tsx"],
}

# Database Configuration
SQLALCHEMY_DATABASE_URI = os.getenv(
    "DATABASE_URL", f"sqlite:///{BASE_DIR / 'site.db'}"
)
SQLALCHEMY_TRACK_MODIFICATIONS = False

# JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-secret")
JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)
