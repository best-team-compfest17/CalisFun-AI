# -------- Stage 1: Builder --------
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies (untuk compile wheels dsb)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
 && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install dependencies ke folder lokal (biar clean di runtime)
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt --target /app/deps


# -------- Stage 2: Runtime --------
FROM python:3.11-slim AS runtime

WORKDIR /app

# Install runtime dependencies (supaya OpenCV bisa jalan)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
 && rm -rf /var/lib/apt/lists/*

# Copy dependencies dari builder
COPY --from=builder /app/deps /usr/local/lib/python3.11/site-packages

# Copy source code
COPY . .

# Pre-download TrOCR model saat build (cache di folder lokal)
RUN python -c "from transformers import TrOCRProcessor, VisionEncoderDecoderModel; \
    TrOCRProcessor.from_pretrained('microsoft/trocr-base-printed', cache_dir='/app/image-ocr/trocr_cache'); \
    VisionEncoderDecoderModel.from_pretrained('microsoft/trocr-base-printed', cache_dir='/app/image-ocr/trocr_cache')"

# Expose port (sesuai Flask/Gunicorn app)
EXPOSE 5000

# Gunicorn untuk production (pakai app-prod.py)
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app-prod:app"]