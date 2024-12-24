"""Logging configuration for Redis Data Structures."""

import logging
import sys
from typing import Optional


def setup_logging(
    level: int = logging.INFO,
    format_string: Optional[str] = None,
    filename: Optional[str] = None,
) -> logging.Logger:
    """Set up logging configuration.

    Args:
        level: The logging level (default: logging.INFO)
        format_string: Custom format string for logs
        filename: Optional file to write logs to

    Returns:
        logging.Logger: Configured logger instance
    """
    if format_string is None:
        format_string = "[%(asctime)s] %(levelname)s - %(name)s - %(message)s"

    logger = logging.getLogger("redis_data_structures")
    logger.setLevel(level)

    if not logger.handlers:
        handler = logging.FileHandler(filename) if filename else logging.StreamHandler(sys.stdout)

        formatter = logging.Formatter(format_string)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


# Default logger instance
logger = setup_logging()
