"""
utils.py

Environment helper and small utilities.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env (if present)
load_dotenv()


def get_env(key: str, default: str | None = None) -> str | None:
    """
    Fetches the value of an environment variable.

    Args:
        key: The environment variable name
        default: fallback value

    Returns:
        string value or default (or None)
    """
    return os.getenv(key, default)