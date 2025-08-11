# Base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy model cache (if pre-downloaded)
COPY trocr_cache /app/trocr_cache

# Copy app code
COPY app.py .

# Expose port
EXPOSE 5000

# Run Flask
CMD ["python", "app.py"]