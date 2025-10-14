# owlow_project/analyzer.py
"""
Performs property analysis using optional LLM or embedding model.
Lazy-loads heavy components only when analyze() is called.
"""

from __future__ import annotations
import importlib
from typing import List, Dict, Any
from .utils import logger, timeit
from .config import Config

class PropertyAnalyzer:
    def __init__(self, use_llm: bool = False, logger=logger):
        self.use_llm = use_llm
        self.logger = logger
        self.cfg = Config.get()
        self.embedder = None
        self.openai_client = None

    def _load_models(self):
        """Lazy-load embedding or LLM models."""
        if self.use_llm:
            try:
                openai_mod = importlib.import_module("openai")
                self.openai_client = openai_mod.OpenAI(api_key=self.cfg.OPENAI_API_KEY)
                self.logger.info("LLM model ready: %s", self.cfg.LLM_MODEL)
            except Exception as e:
                self.logger.error("Failed to initialize LLM: %s", e)
                self.use_llm = False
        else:
            try:
                sentence_mod = importlib.import_module("sentence_transformers")
                self.embedder = sentence_mod.SentenceTransformer("all-MiniLM-L6-v2")
                self.logger.info("SentenceTransformer loaded.")
            except Exception as e:
                self.logger.warning("Falling back: embedding model unavailable (%s)", e)

    @timeit
    def analyze(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Perform text analysis or semantic embedding."""
        if not items:
            return []

        self._load_models()

        if self.use_llm and self.openai_client:
            results = []
            for item in items:
                prompt = f"Analyze this property description briefly: {item['clean_description']}"
                try:
                    resp = self.openai_client.chat.completions.create(
                        model=self.cfg.LLM_MODEL,
                        messages=[{"role": "user", "content": prompt}],
                        max_tokens=40
                    )
                    summary = resp.choices[0].message.content.strip()
                except Exception as e:
                    self.logger.warning("LLM analysis failed: %s", e)
                    summary = "Analysis unavailable."
                item["analysis_summary"] = summary
                results.append(item)
            return results

        elif self.embedder:
            texts = [it["clean_description"] for it in items]
            embeddings = self.embedder.encode(texts)
            for i, emb in enumerate(embeddings):
                items[i]["embedding"] = emb.tolist()
            return items

        else:
            self.logger.warning("No model available; returning unmodified items.")
            return items
