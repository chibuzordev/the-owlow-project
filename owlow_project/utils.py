# owlow_project/utils.py
"""
Small helpers and logging utilities.
Keep this module lightweight so it is safe for import in many places.
"""

from __future__ import annotations
import logging
import sys
import time
from typing import Callable, Any, Optional
from functools import wraps

def get_logger(name: str = "owlow") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)s %(name)s: %(message)s", "%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger

logger = get_logger()

def timeit(fn: Callable) -> Callable:
    """Simple timing decorator for functions"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        start = time.time()
        try:
            return fn(*args, **kwargs)
        finally:
            elapsed = time.time() - start
            logger.info("%s executed in %.3fs", fn.__name__, elapsed)
    return wrapper

def safe_request_json(resp) -> Optional[dict]:
    """Given a requests.Response-like object, attempt to parse JSON safely."""
    try:
        return resp.json()
    except Exception:
        logger.exception("Failed to parse JSON from response")
        return None
