import requests

api_key = "helloworld"  # API key gratis -> login di web api ocr space ini
url = "https://api.ocr.space/parse/image"
with open("handwritten/halo.png", "rb") as image_file:
    response = requests.post(
        url,
        files={"file": image_file},
        data={"apikey": api_key, "language": "ind"}
    )
print(response.json()["ParsedResults"][0]["ParsedText"])