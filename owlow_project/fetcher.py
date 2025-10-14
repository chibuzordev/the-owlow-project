# owlow_project/fetcher.py
"""
Fetches property data from an API endpoint or local fallback.
"""

from __future__ import annotations
import requests
from typing import List, Dict, Any
from .utils import logger, safe_request_json, timeit

class DataFetcher:
    def __init__(self, api_url: str, logger=logger):
        self.api_url = api_url
        self.logger = logger

    @timeit
    def fetch(self, max_items: int = 10) -> List[Dict[str, Any]]:
        """Fetch data from API or fallback if unavailable."""
        try:
            resp = requests.get(self.api_url, timeout=10)
            data = safe_request_json(resp)
            if not data:
                raise ValueError("Empty data returned from API.")
            items = data[:max_items]
            self.logger.info("Fetched %d items", len(items))
            return items
        except Exception as e:
            self.logger.warning("Falling back to mock data: %s", e)
            return self._mock_data(max_items)

    def _mock_data(self, n: int) -> List[Dict[str, Any]]:
        """Fallback data for local dev or API failure."""
        return [
            {
                "id": i,
                "title": f"Cozy Apartment #{i}",
                "description": f"Beautiful 2-bedroom apartment in city center, unit {i}.",
                "price": 50000 + i * 1000,
                "location": "Lagos",
                "images": []
            }
            for i in range(1, n + 1)
        ]
