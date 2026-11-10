# Multi-stage Dockerfile for BrandSentinel AI
# Stage 1: Runtime environment with Python and system libraries for OpenCV/PyMuPDF
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Install system dependencies required for OpenCV and Tesseract OCR
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

# Copy compiled frontend production build (already built with Vite)
COPY frontend/dist /app/frontend/dist

# Copy sample test documents
COPY sample_documents /app/sample_documents

# Create uploads directory
RUN mkdir -p /app/backend/uploads

# Expose server port
EXPOSE 8000

# Working directory set to backend
WORKDIR /app/backend

# Start full-stack server serving both API and React SPA
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

