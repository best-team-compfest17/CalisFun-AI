import requests

url = "http://localhost:5000/ocr"
files = {"file": open("./handwritten/test-2.png", "rb")}  # Ganti dengan path gambar yang diinginkan
response = requests.post(url, files=files)

print(response.json())