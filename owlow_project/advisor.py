# owlow_project/advisor.py
"""
Optional helper that summarizes analysis results into short, actionable advice.
Small, safe, and importable without heavy deps.
"""

from __future__ import annotations
from typing import List, Dict, Any
from .utils import logger

class Advisor:
    def __init__(self, logger=logger):
        self.logger = logger

    def summarize(self, analysis: List[Dict[str, Any]], top_n: int = 3) -> Dict[str, Any]:
        """Return a small human-friendly summary and top recommendations."""
        if not analysis:
            return {"message": "No analysis available."}

        # Pick top by score if available, else by price_norm (lower price_norm -> higher desirability)
        sorted_items = sorted(
            analysis,
            key=lambda x: x.get("score", -(1.0 / (x.get("price_norm", 1.0) + 1e-6))),
            reverse=True
        )

        top = sorted_items[:top_n]
        summary = {
            "count": len(analysis),
            "top_recommendations": [
                {"id": it.get("id"), "title": it.get("title"), "score": it.get("score", None)}
                for it in top
            ],
            "note": "Scores are heuristic. For deeper insight enable LLM analysis (LLM_ENABLED=true)."
        }
        self.logger.info("Advisor produced summary for %d items", len(analysis))
        return summary
