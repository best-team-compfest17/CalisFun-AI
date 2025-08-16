from flask import Flask, request, jsonify
from PIL import Image
import cv2, numpy as np, os
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from openai import AzureOpenAI
from dotenv import load_dotenv
from flask_cors import CORS

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": os.getenv("CORS_ALLOW_ORIGINS", "*")}})
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv("MAX_UPLOAD_MB", "10")) * 1024 * 1024

# --- Model config ---
MODEL_CACHE_DIR = os.getenv("MODEL_CACHE_DIR", "/app/image-ocr/trocr_cache")
MODEL_ID = os.getenv("TROCR_MODEL_ID", "microsoft/trocr-base-printed")
os.makedirs(MODEL_CACHE_DIR, exist_ok=True)

def load_model():
    # Coba pakai cache lokal dulu (cepat di startup)
    try:
        processor = TrOCRProcessor.from_pretrained(MODEL_CACHE_DIR, local_files_only=True)
        model = VisionEncoderDecoderModel.from_pretrained(MODEL_CACHE_DIR, local_files_only=True)
        return processor, model
    except Exception:
        # Fallback: download dari Hugging Face ke cache (butuh internet saat runtime)
        processor = TrOCRProcessor.from_pretrained(MODEL_ID, cache_dir=MODEL_CACHE_DIR)
        model = VisionEncoderDecoderModel.from_pretrained(MODEL_ID, cache_dir=MODEL_CACHE_DIR)
        return processor, model

trocr_processor, trocr_model = load_model()

def preprocess_image(image_bytes):
    image = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    return cv2.cvtColor(enhanced, cv2.COLOR_GRAY2RGB)

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
        pixel_values = trocr_processor(pil_image, return_tensors="pt").pixel_values
        generated_ids = trocr_model.generate(pixel_values)
        text = trocr_processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
        return jsonify({"text": text})
    except Exception as e:
        return jsonify({"error": str(e), "message": "Gagal memproses gambar"}), 500

# --- Azure OpenAI ---
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    api_version=os.getenv("AZURE_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)
DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-35-turbo")

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json or {}
        user_message = data.get('message')
        if not user_message:
            return jsonify({"error": "Message is required"}), 400

        response = client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": "Anda adalah asisten yang membantu."},
                {"role": "user", "content": user_message}
            ]
        )
        bot_reply = response.choices[0].message.content
        tokens_used = getattr(response, "usage", None).total_tokens if getattr(response, "usage", None) else None
        return jsonify({"reply": bot_reply, "tokens_used": tokens_used})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Gunicorn akan dipakai di container (lihat Dockerfile), ini hanya untuk dev lokal.
    app.run(host='0.0.0.0', port=int(os.getenv("PORT", "5000")), debug=True)