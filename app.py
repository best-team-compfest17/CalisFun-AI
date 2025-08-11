from flask import Flask, request, jsonify
from PIL import Image
import io
import cv2
import numpy as np
import os
from transformers import TrOCRProcessor, VisionEncoderDecoderModel

from flask import Flask, request, jsonify
from openai import AzureOpenAI
import os
from dotenv import load_dotenv
from flask_cors import CORS

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# # --- Load Model (Cached) ---
MODEL_CACHE_DIR = "image-ocr/trocr_cache"
os.makedirs(MODEL_CACHE_DIR, exist_ok=True)

def load_model():
    processor = TrOCRProcessor.from_pretrained(MODEL_CACHE_DIR)
    model = VisionEncoderDecoderModel.from_pretrained(MODEL_CACHE_DIR)
    return processor, model

trocr_processor, trocr_model = load_model()

# # --- Preprocessing ---
def preprocess_image(image_bytes):
    image = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    # Konversi kembali ke 3 channel (RGB)
    return cv2.cvtColor(enhanced, cv2.COLOR_GRAY2RGB)  # Perubahan di sini

# # --- API Endpoint ---
@app.route('/ocr', methods=['POST'])
def ocr():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Empty filename"}), 400

    try:
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
    
    except Exception as e:
        return jsonify({"error": str(e), "message": "Gagal memproses gambar"}), 500


# Konfigurasi Azure OpenAI
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_KEY"),  # Simpan di .env
    api_version=os.getenv("AZURE_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

# Model yang digunakan
DEPLOYMENT_NAME = "gpt-35-turbo"  # Ganti dengan nama deployment Anda

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('message')

        if not user_message:
            return jsonify({"error": "Message is required"}), 400

        # Panggil Azure OpenAI
        response = client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": "Anda adalah asisten yang membantu."},
                {"role": "user", "content": user_message}
            ]
        )

        # Ambil balasan
        bot_reply = response.choices[0].message.content

        return jsonify({
            "reply": bot_reply,
            "tokens_used": response.usage.total_tokens
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)