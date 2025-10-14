# main.py
"""
Entrypoint for local development.
Render will use the Dockerfile to run the container (which should call `uvicorn main:app`).
"""

from __future__ import annotations
import uvicorn
from owlow_project.server import app
from owlow_project.config import Config

def run():
    cfg = Config.get()
    uvicorn.run(app, host=cfg.HOST, port=cfg.PORT, log_level="info")

if __name__ == "__main__":
    run()
