# owlow_project/server.py
"""
FastAPI server wrapper. Keep this file import-safe (no heavy model imports here).
Heavy components are imported lazily inside the endpoint handlers.
"""

from __future__ import annotations
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import importlib
from .config import Config
from .utils import logger, timeit

app = FastAPI(title="The Owlow Project API", version="0.1.0")
cfg = Config.get()

class RunPipelinePayload(BaseModel):
    source: Optional[str] = "api"
    max_items: Optional[int] = 10
    run_llm: Optional[bool] = None  # if provided, overrides env LLM_ENABLED

@app.get("/health")
def health() -> Dict[str, Any]:
    """Simple health check that is safe to run on startup."""
    return {"status": "ok", "service": "The Owlow Project", "llm_enabled": cfg.LLM_ENABLED}

@app.post("/run_pipeline", response_model=dict)
@timeit
def run_pipeline(payload: RunPipelinePayload = Body(...)):
    """
    Orchestrates the pipeline.
    We import modules lazily here so that importing server doesn't load heavy ML models.
    """
    run_llm = cfg.LLM_ENABLED if payload.run_llm is None else payload.run_llm
    logger.info("Starting pipeline. source=%s max_items=%s run_llm=%s",
                payload.source, payload.max_items, run_llm)

    try:
        # Lazy import of pipeline components to avoid heavy imports at module load
        fetcher_mod = importlib.import_module("owlow_project.fetcher")
        preprocessor_mod = importlib.import_module("owlow_project.preprocessor")
        analyzer_mod = importlib.import_module("owlow_project.analyzer")
        recommender_mod = importlib.import_module("owlow_project.recommender")
    except ModuleNotFoundError as e:
        logger.error("Pipeline module not found: %s", e)
        raise HTTPException(status_code=500, detail="Pipeline modules missing. Deploy incomplete.")

    # Instantiate classes
    fetcher = fetcher_mod.DataFetcher(cfg.OWL_API_URL, logger=logger)
    preprocessor = preprocessor_mod.Preprocessor(logger=logger)
    analyzer = analyzer_mod.PropertyAnalyzer(use_llm=run_llm, logger=logger)
    recommender = recommender_mod.Recommender(logger=logger)

    # Step 1: fetch
    items = fetcher.fetch(max_items=payload.max_items)

    # Step 2: preprocess
    processed = preprocessor.transform(items)

    # Step 3: analyze (may invoke LLM if enabled)
    analysis = analyzer.analyze(processed)

    # Step 4: recommend / rank
    recommendations = recommender.recommend(analysis)

    # Minimal response: counts + sample
    sample = recommendations[:3] if isinstance(recommendations, list) else recommendations
    return {
        "status": "completed",
        "counts": {
            "fetched": len(items),
            "processed": len(processed),
            "analyzed": len(analysis) if hasattr(analysis, "__len__") else "1",
            "recommended": len(recommendations) if hasattr(recommendations, "__len__") else "1",
        },
        "sample": sample
    }

