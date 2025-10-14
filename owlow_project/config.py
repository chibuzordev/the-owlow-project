# owlow_project/config.py
"""
Centralized environment/config loader.
This module is intentionally lightweight and safe to import at module-level.
Use Config.get() to access runtime configuration.
"""

from __future__ import annotations
import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

load_dotenv()  # safe: will silently ignore if no .env present

@dataclass(frozen=True)
class Config:
    OPENAI_API_KEY: Optional[str]
    OWL_API_URL: str
    LLM_ENABLED: bool
    LLM_MODEL: str
    MAX_IMAGE_SIZE: int
    MAX_IMAGES: int
    HOST: str
    PORT: int
    DEBUG: bool

    @staticmethod
    def get() -> "Config":
        # Provide reasonable defaults for local dev; production should set env vars on the host
        return Config(
            OPENAI_API_KEY=os.getenv("OPENAI_API_KEY"),
            OWL_API_URL=os.getenv("OWL_API_URL", "https://example.com/api/listings"),
            LLM_ENABLED=os.getenv("LLM_ENABLED", "false").lower() in ("1", "true", "yes"),
            LLM_MODEL=os.getenv("LLM_MODEL", "gpt-4o-mini"),
            MAX_IMAGE_SIZE=int(os.getenv("MAX_IMAGE_SIZE", "512")),
            MAX_IMAGES=int(os.getenv("MAX_IMAGES", "2")),
            HOST=os.getenv("HOST", "0.0.0.0"),
            PORT=int(os.getenv("PORT", "8000")),
            DEBUG=os.getenv("DEBUG", "false").lower() in ("1", "true", "yes"),
        )
