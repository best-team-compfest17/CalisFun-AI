from flask import Flask, request, jsonify
from PIL import Image
import io
import cv2
import numpy as np
import os
from transformers import TrOCRProcessor, VisionEncoderDecoderModel

app = Flask(__name__)

# --- Load Model (Cached) ---
MODEL_CACHE_DIR = "trocr_cache"
os.makedirs(MODEL_CACHE_DIR, exist_ok=True)

def load_model():
    processor = TrOCRProcessor.from_pretrained(MODEL_CACHE_DIR)
    model = VisionEncoderDecoderModel.from_pretrained(MODEL_CACHE_DIR)
    return processor, model

trocr_processor, trocr_model = load_model()

# --- Preprocessing ---
def preprocess_image(image_bytes):
    image = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    return enhanced

# --- API Endpoint ---
@app.route('/ocr', methods=['POST'])
def ocr():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Empty filename"}), 400

    # Preprocess image
    image_bytes = file.read()
    processed_image = preprocess_image(image_bytes)
    
    # Convert to PIL Image
    pil_image = Image.fromarray(processed_image)
    
    # OCR
    pixel_values = trocr_processor(pil_image, return_tensors="pt").pixel_values
    generated_ids = trocr_model.generate(pixel_values)
    text = trocr_processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
    
    return jsonify({"text": text})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)