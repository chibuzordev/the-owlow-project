# Dockerfile - optimized for smaller image size and Render's limits
FROM python:3.11-slim

# Set non-root user for better security (optional but helpful)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create app directory
WORKDIR /app

# Install minimal system deps required by some Python packages
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential git curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first to leverage layer caching
COPY requirements.txt /app/requirements.txt

# Install Python deps without cache to reduce image size
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy application code
COPY . /app

# Ensure the app is not starting heavy models at import time
ENV HOST=0.0.0.0
ENV PORT=8000
ENV LLM_ENABLED=false

# Expose port and set a simple health command
EXPOSE 8000

# Use a simple command that runs uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
