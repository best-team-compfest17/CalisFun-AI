import os
import cv2
import numpy as np
from PIL import Image
from transformers import TrOCRProcessor, VisionEncoderDecoderModel

# --- Path Configuration ---
HANDWRITTEN_IMAGES_DIR = "handwritten"
OUTPUT_TEXT_DIR = "result"
MODEL_CACHE_DIR = "trocr_cache"  # Folder untuk menyimpan model
os.makedirs(OUTPUT_TEXT_DIR, exist_ok=True)
os.makedirs(MODEL_CACHE_DIR, exist_ok=True)

# --- 1. Load or Cache TrOCR Model ---
def load_trocr_model():
    # Cek apakah model sudah di-cache
    if not os.path.exists(os.path.join(MODEL_CACHE_DIR, "processor")) or \
       not os.path.exists(os.path.join(MODEL_CACHE_DIR, "model")):
        
        print("⚡ Downloading TrOCR model (first time only)...")
        processor = TrOCRProcessor.from_pretrained("microsoft/trocr-base-handwritten")
        model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-base-handwritten")
        
        # Simpan ke disk
        processor.save_pretrained(MODEL_CACHE_DIR)
        model.save_pretrained(MODEL_CACHE_DIR)
    else:
        # Load dari cache
        processor = TrOCRProcessor.from_pretrained(MODEL_CACHE_DIR)
        model = VisionEncoderDecoderModel.from_pretrained(MODEL_CACHE_DIR)
    
    return processor, model

# Load model sekali di awal
trocr_processor, trocr_model = load_trocr_model()

# --- 2. TrOCR Recognition (Using Cached Model) ---
def trocr_recognize(image_path):
    image = Image.open(image_path).convert("RGB")
    pixel_values = trocr_processor(image, return_tensors="pt").pixel_values
    generated_ids = trocr_model.generate(pixel_values)
    return trocr_processor.batch_decode(generated_ids, skip_special_tokens=True)[0]

# --- Preprocessing ---
def preprocess_image(image_path):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    return enhanced

# --- Main Loop ---
for filename in os.listdir(HANDWRITTEN_IMAGES_DIR):
    if filename.endswith((".png", ".jpg", ".jpeg")):
        image_path = os.path.join(HANDWRITTEN_IMAGES_DIR, filename)
        
        # Preprocess image
        processed_image = preprocess_image(image_path)
        temp_path = os.path.join(OUTPUT_TEXT_DIR, f"processed_{filename}")
        cv2.imwrite(temp_path, processed_image)
        
        # Recognize text
        text = trocr_recognize(temp_path)
        
        # Save to text file
        output_text_path = os.path.join(OUTPUT_TEXT_DIR, f"{os.path.splitext(filename)[0]}.txt")
        with open(output_text_path, "w", encoding="utf-8") as f:
            f.write(text)
        
        print(f"Processed: {filename} -> {output_text_path}")

print("✅ All images processed!")