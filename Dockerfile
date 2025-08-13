FROM python:3.10-slim

# Sistem dep. untuk OpenCV, dll.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential git ffmpeg libsm6 libxext6 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install deps dulu (layer cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Siapkan cache model (dibundel ke image agar startup cepat)
ARG TROCR_MODEL_ID=microsoft/trocr-base-printed
ENV TROCR_MODEL_ID=${TROCR_MODEL_ID}
ENV MODEL_CACHE_DIR=/app/image-ocr/trocr_cache
RUN mkdir -p ${MODEL_CACHE_DIR} && python - <<'PY'
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
import os
model_id = os.getenv("TROCR_MODEL_ID", "microsoft/trocr-base-printed")
cache_dir = os.getenv("MODEL_CACHE_DIR", "/app/image-ocr/trocr_cache")
TrOCRProcessor.from_pretrained(model_id, cache_dir=cache_dir)
VisionEncoderDecoderModel.from_pretrained(model_id, cache_dir=cache_dir)
print("Downloaded", model_id, "to", cache_dir)
PY

# Copy source
COPY . .

# Expose & start via gunicorn
ENV PORT=5000
EXPOSE 5000
# Worker gthread: cocok utk CPU-bound ringan + I/O
CMD exec gunicorn -w ${GUNICORN_WORKERS:-2} -k gthread --threads ${GUNICORN_THREADS:-8} \
  -t ${GUNICORN_TIMEOUT:-120} -b 0.0.0.0:${PORT} app:app
