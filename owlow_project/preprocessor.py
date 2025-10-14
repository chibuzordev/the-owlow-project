# owlow_project/preprocessor.py
"""
Lightweight preprocessing and feature extraction.
"""

from __future__ import annotations
import re
from typing import List, Dict, Any
import numpy as np
from .utils import logger, timeit

class Preprocessor:
    def __init__(self, logger=logger):
        self.logger = logger

    @staticmethod
    def _clean_text(text: str) -> str:
        return re.sub(r"[^A-Za-z0-9\s.,-]", "", text.strip())

    @timeit
    def transform(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Clean descriptions and basic normalization."""
        processed = []
        for item in items:
            desc = item.get("description", "")
            clean_desc = self._clean_text(desc)
            item["clean_description"] = clean_desc.lower()
            item["price_norm"] = float(item["price"]) / 100000
            processed.append(item)
        self.logger.info("Preprocessed %d items", len(processed))
        return processed
