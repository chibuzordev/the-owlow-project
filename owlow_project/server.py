# owlow_project/server.py
from __future__ import annotations
from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
from typing import Optional, Dict, Any
import importlib
from .config import Config
from .utils import logger, timeit

# 1️⃣ Define the payload BEFORE app = FastAPI()
class RunPipelinePayload(BaseModel):
    source: Optional[str] = "api"
    max_items: Optional[int] = 10
    run_llm: Optional[bool] = None  # overrides env LLM_ENABLED

# 2️⃣ Then create app
app = FastAPI(title="The Owlow Project API", version="0.1.0")
cfg = Config.get()

@app.get("/health")
def health() -> Dict[str, Any]:
    return {"status": "ok", "service": "The Owlow Project", "llm_enabled": cfg.LLM_ENABLED}

@app.post("/run_pipeline")
@timeit
def run_pipeline(payload: RunPipelinePayload = Body(...)):
    """Orchestrate the pipeline."""
    run_llm = cfg.LLM_ENABLED if payload.run_llm is None else payload.run_llm
    logger.info("Starting pipeline. source=%s max_items=%s run_llm=%s",
                payload.source, payload.max_items, run_llm)

    try:
        fetcher_mod = importlib.import_module("owlow_project.fetcher")
        preprocessor_mod = importlib.import_module("owlow_project.preprocessor")
        analyzer_mod = importlib.import_module("owlow_project.analyzer")
        recommender_mod = importlib.import_module("owlow_project.recommender")
    except ModuleNotFoundError as e:
        logger.error("Pipeline module not found: %s", e)
        raise HTTPException(status_code=500, detail="Pipeline modules missing. Deploy incomplete.")

    fetcher = fetcher_mod.DataFetcher(cfg.OWL_API_URL, logger=logger)
    preprocessor = preprocessor_mod.Preprocessor(logger=logger)
    analyzer = analyzer_mod.PropertyAnalyzer(use_llm=run_llm, logger=logger)
    recommender = recommender_mod.Recommender(logger=logger)

    items = fetcher.fetch(max_items=payload.max_items)
    processed = preprocessor.transform(items)
    analysis = analyzer.analyze(processed)
    recommendations = recommender.recommend(analysis)
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

# --- Fix for Pydantic forward-ref bug on FastAPI + Pydantic v2 ---
try:
    RunPipelinePayload.model_rebuild(force=True)
except Exception as e:
    from .utils import logger
    logger.warning(f"Schema rebuild failed: {e}")
# -----------------------------------------------------------------
