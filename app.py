# Import Libraries

from flask import Flask, request, jsonify
from PIL import Image
import cv2, numpy as np, os
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from openai import AzureOpenAI
from dotenv import load_dotenv
from flask_cors import CORS

# Get the environment variable

load_dotenv()

# Create Flask App

def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": os.getenv("CORS_ALLOW_ORIGINS", "*")}})
    app.config['MAX_CONTENT_LENGTH'] = int(os.getenv("MAX_UPLOAD_MB", "10")) * 1024 * 1024

    # Initialize services
    app.trocr_processor, app.trocr_model = load_model()
    app.azure_client = init_azure_client()
    
    register_routes(app)
    return app

# Load or Create Microsoft TrOCR Model

def load_model():
    MODEL_CACHE_DIR = os.getenv("MODEL_CACHE_DIR", "/app/image-ocr/trocr_cache")
    MODEL_ID = os.getenv("TROCR_MODEL_ID", "microsoft/trocr-base-printed")
    os.makedirs(MODEL_CACHE_DIR, exist_ok=True)

    try:
        processor = TrOCRProcessor.from_pretrained(MODEL_CACHE_DIR, local_files_only=True)
        model = VisionEncoderDecoderModel.from_pretrained(MODEL_CACHE_DIR, local_files_only=True)
        return processor, model
    except Exception:
        processor = TrOCRProcessor.from_pretrained(MODEL_ID, cache_dir=MODEL_CACHE_DIR)
        model = VisionEncoderDecoderModel.from_pretrained(MODEL_ID, cache_dir=MODEL_CACHE_DIR)
        return processor, model

# Init Setup Azure

def init_azure_client():
    return AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_KEY"),
        api_version=os.getenv("AZURE_API_VERSION"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
    )

# Register the Flask Routes

def register_routes(app):
    @app.route('/healthz', methods=['GET'])
    def healthz():
        return jsonify({"status": "ok"}), 200

    @app.route('/ocr', methods=['POST'])
    def ocr():
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "Empty filename"}), 400
        
        try:
            image_bytes = file.read()
            processed_image = preprocess_image(image_bytes)
            pil_image = Image.fromarray(processed_image)
            pixel_values = app.trocr_processor(pil_image, return_tensors="pt").pixel_values
            generated_ids = app.trocr_model.generate(pixel_values)
            text = app.trocr_processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
            return jsonify({"text": text})
        except Exception as e:
            return jsonify({"error": str(e), "message": "Gagal memproses gambar"}), 500

    @app.route('/chat', methods=['POST'])
    def chat():
        try:
            data = request.json or {}
            user_message = data.get('message')
            if not user_message:
                return jsonify({"error": "Message is required"}), 400

            response = app.azure_client.chat.completions.create(
                model=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-35-turbo"),
                messages=[
                    {"role": "system", "content": "Anda adalah asisten yang membantu."},
                    {"role": "user", "content": user_message}
                ]
            )
            return jsonify({
                "reply": response.choices[0].message.content,
                "tokens_used": response.usage.total_tokens if response.usage else None
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500

# Preprocessing the image ocr

def preprocess_image(image_bytes):
    image = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    return cv2.cvtColor(enhanced, cv2.COLOR_GRAY2RGB)

# Create the flask app and expose the port on 5000

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv("PORT", "5000")), debug=True)