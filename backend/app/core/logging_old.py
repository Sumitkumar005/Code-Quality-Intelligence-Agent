"""
Logging configuration for the CQIA application.
"""

import logging
import logging.config
from typing import Dict, Any

from app.core.config import settings


def setup_logging() -> None:
    """
    Setup logging configuration for the application.
    """
    logging_config: Dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "json": {
                "format": '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}',
                "datefmt": "%Y-%m-%dT%H:%M:%S%z",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "level": "INFO",
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": "logs/cqia.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "formatter": "detailed",
                "level": "INFO",
            },
            "error_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": "logs/cqia_error.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "formatter": "detailed",
                "level": "ERROR",
            },
        },
        "root": {
            "level": "INFO",
            "handlers": ["console"],
        },
        "loggers": {
            "app": {
                "level": "INFO",
                "handlers": ["console", "file", "error_file"],
                "propagate": False,
            },
            "uvicorn": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False,
            },
            "sqlalchemy": {
                "level": "WARNING",
                "handlers": ["console"],
                "propagate": False,
            },
        },
    }

    # Add file handlers only if not in debug mode or if log files are enabled
    if not settings.DEBUG or settings.LOG_TO_FILE:
        # Ensure logs directory exists
        import os
        os.makedirs("logs", exist_ok=True)

        logging_config["root"]["handlers"].extend(["file", "error_file"])
        logging_config["loggers"]["app"]["handlers"].extend(["file", "error_file"])

    # Use JSON formatter in production
    if not settings.DEBUG:
        logging_config["handlers"]["console"]["formatter"] = "json"

    logging.config.dictConfig(logging_config)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(f"app.{name}")


# Create logs directory if it doesn't exist
import os
os.makedirs("logs", exist_ok=True)
