"""Configuration management for Notion RSS Feed Generator."""

import logging
import os
from pathlib import Path

from dotenv import find_dotenv, load_dotenv

if not find_dotenv():
    print("Warning: .env file not found. Environment variables may be missing.")  # noqa: T201
else:
    load_dotenv()


class Config:
    """Configuration settings for the RSS feed generator.

    Loads environment variables and provides validation for required settings.
    Uses singleton pattern to ensure consistent configuration across the application.
    """

    _instance: "Config | None" = None

    def __new__(cls) -> "Config":
        """Create or return existing singleton instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.initialized = False  # just created, not initialized
        return cls._instance

    def __init__(self) -> None:
        """Initialize configuration by loading environment variables."""
        # Prevent re-initialization of singleton
        if getattr(self, "initialized", False):
            return

        self.NOTION_API_KEY: str = os.getenv("NOTION_API_KEY", "")
        self.NOTION_DATABASE_ID: str = os.getenv("NOTION_DATABASE_ID", "")

        # RSS Feed Configuration
        self.RSS_FEED_PATH: str = os.getenv("RSS_FEED_PATH", "notion_reading_list.xml")
        self.RSS_FEED_TITLE: str = os.getenv("RSS_FEED_TITLE", "Notion Reading List")
        self.RSS_FEED_DESCRIPTION: str = os.getenv(
            "RSS_FEED_DESCRIPTION", "My personal reading list collected in Notion"
        )
        self.RSS_FEED_LINK: str | None = os.getenv("RSS_FEED_LINK")

        # Logging Configuration
        self.LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

        self.initialized = True

    def validate(self) -> list[str]:
        """Validate required configuration settings.

        Returns:
            List of missing or invalid configuration keys.
        """
        errors: list[str] = []
        if not self.NOTION_API_KEY:
            errors.append("NOTION_API_KEY is required")
        if not self.NOTION_DATABASE_ID:
            errors.append("NOTION_DATABASE_ID is required")
        return errors

    @classmethod
    def get_instance(cls) -> "Config":
        """Get the singleton configuration instance.

        Returns:
            The singleton Config instance.
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance


def configure_logging(
    *,
    log_level: str | None = None,
    verbose: bool = False,
    log_to_file: bool = True,
    log_file_path: str | Path = "logs/app.log",
) -> None:
    """Configure logging for the application.

    Args:
        log_level: Logging level string (e.g., "DEBUG", "INFO", "WARNING", "ERROR").
                  If None, uses Config's LOG_LEVEL or "INFO" as default.
        verbose: If True, sets logging level to DEBUG (overrides log_level).
        log_to_file: Whether to write logs to a file.
        log_file_path: Path to the log file (default: "logs/app.log").
    """
    # Determine the logging level
    if verbose:
        level = logging.DEBUG
    elif log_level:
        level = getattr(logging, log_level.upper(), logging.INFO)
    else:
        # Try to get from config, fallback to INFO
        try:
            config = Config.get_instance()
            level = getattr(logging, config.LOG_LEVEL.upper(), logging.INFO)
        except (AttributeError, ValueError):
            level = logging.INFO

    # Clear existing handlers to avoid duplication
    root_logger = logging.getLogger()
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    # Configure handlers
    handlers: list[logging.Handler] = [logging.StreamHandler()]

    if log_to_file:
        log_dir = Path(log_file_path).parent
        log_dir.mkdir(exist_ok=True)
        file_handler = logging.FileHandler(log_file_path)
        handlers.append(file_handler)

    # Set up logging configuration
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=handlers,
    )
