from flask import request, jsonify
import os

from openai import AzureOpenAI
import os

# Konfigurasi Azure OpenAI
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_KEY"),  # Simpan di .env
    api_version=os.getenv("AZURE_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

# Model yang digunakan
DEPLOYMENT_NAME = "gpt-35-turbo"  # Ganti dengan nama deployment Anda

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