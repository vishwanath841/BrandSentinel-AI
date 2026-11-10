# ==============================================================================
# Multi-stage Dockerfile for BrandSentinel AI
# ==============================================================================

# ─── Stage 1: Build React Frontend ───────────────────────────────────────────
FROM node:20-slim AS frontend-builder
WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm install

COPY frontend/ ./
RUN npm run build

# ─── Stage 2: Runtime Environment with Python and System Dependencies ─────────
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Install system dependencies required for OpenCV, PyMuPDF, and Tesseract OCR
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    tesseract-ocr \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python backend dependencies
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Copy backend application source code
COPY backend /app/backend

# Copy compiled frontend from Stage 1
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist

# Copy sample test documents
COPY sample_documents /app/sample_documents

# Create uploads directory
RUN mkdir -p /app/backend/uploads

# Expose default port
EXPOSE 8000

WORKDIR /app/backend

# Start uvicorn with dynamic PORT support for Render, Railway, Cloud Run
CMD ["sh", "-c", "python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
