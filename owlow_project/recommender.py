# owlow_project/recommender.py
"""
Recommender based on similarity or heuristic ranking.
"""

from __future__ import annotations
from typing import List, Dict, Any
import numpy as np
from .utils import logger, timeit

class Recommender:
    def __init__(self, logger=logger):
        self.logger = logger

    @staticmethod
    def _similarity(a: np.ndarray, b: np.ndarray) -> float:
        """Compute cosine similarity."""
        if np.linalg.norm(a) == 0 or np.linalg.norm(b) == 0:
            return 0.0
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

    @timeit
    def recommend(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Simple ranking by price or embedding proximity."""
        if not items:
            return []

        if "embedding" in items[0]:
            ref = np.array(items[0]["embedding"])
            for item in items:
                vec = np.array(item.get("embedding", ref))
                item["score"] = self._similarity(ref, vec)
        else:
            for item in items:
                item["score"] = 1.0 / (item.get("price_norm", 1.0) + 1e-6)

        ranked = sorted(items, key=lambda x: x["score"], reverse=True)
        self.logger.info("Ranked %d items", len(ranked))
        return ranked
