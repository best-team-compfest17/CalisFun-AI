import requests
import os

# 1. Ganti dengan endpoint dan key Anda
endpoint = os.getenv("AZURE_ENDPOINT")
subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY")

# 2. Baca gambar sebagai binary (bytes)
image_path = "text/test-1.png"  # Ganti dengan path gambar Anda
with open(image_path, "rb") as image_file:
    image_bytes = image_file.read()

# 3. Request ke API Azure
headers = {
    "Ocp-Apim-Subscription-Key": subscription_key,
    "Content-Type": "application/octet-stream"  # Penting untuk format binary
}
params = {
    "language": "en",  # Bahasa Inggris
    "detectOrientation": "true"  # Auto-detect orientasi teks
}


try:
    response = requests.post(endpoint, headers=headers, params=params, data=image_bytes)
    # response.raise_for_status()  # Cek error HTTP
    
    # Debug: Cetak status code dan respons mentah
    print(f"Status Code: {response.status_code}")
    print(f"Raw Response: {response.text}")
    
    result = response.json()
    print("Hasil OCR:")
    
    # Perbaikan typo: "regions" (bukan "regions")
    for region in result.get("regions", []):
        for line in region.get("lines", []):
            print(" ".join([word.get("text", "") for word in line.get("words", [])]))
            
except requests.exceptions.RequestException as e:
    print(f"Error HTTP: {e}")
except Exception as e:
    print(f"Error Lain: {e}")