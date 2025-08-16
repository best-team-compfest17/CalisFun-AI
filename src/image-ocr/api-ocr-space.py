import requests

api_key = "helloworld"  # Use your free api key by sign in on the api.ocr.space
url = "https://api.ocr.space/parse/image"
with open("handwritten/halo.png", "rb") as image_file:
    response = requests.post(
        url,
        files={"file": image_file},
        data={"apikey": api_key, "language": "ind"}
    )
print(response.json()["ParsedResults"][0]["ParsedText"])