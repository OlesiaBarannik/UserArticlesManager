import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()


class Config:
    """Configuration class to store environment-specific settings for the application."""

    SQLALCHEMY_DATABASE_URI: str = os.getenv(
        "DATABASE_URL", ""
    )  # Default to an empty string
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    JWT_SECRET_KEY: str = os.getenv("SECRET_KEY", "")  # Default to an empty string
    JWT_ACCESS_TOKEN_EXPIRES: timedelta = timedelta(hours=1)
