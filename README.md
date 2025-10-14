# The Owlow Project

Purpose: small API that ingests property listings, analyzes descriptions/images, and produces recommendation tables.

Quickstart (developer):
1. Copy `.env.example` -> `.env` and set values.
2. Install: `pip install -r requirements.txt`
3. Run (dev): `uvicorn main:app --reload --host 0.0.0.0 --port 8000`
4. Endpoints:
   - GET /health -> service health
   - POST /run_pipeline -> run fetch -> preprocess -> analyze -> export (see README for payload)

Deployment: The repo contains a `Dockerfile` and `render.yaml` suited for Render's Docker deployment.

Secrets: Put API keys in the hosting platform environment variables, not in the repo.
