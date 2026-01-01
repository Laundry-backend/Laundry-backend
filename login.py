import requests
import json

APP_ID = "0ygkstU1AovdDXtI65mok181GCCY87EF"
APP_SECRET = "0UZMVs2oaSoFiYcqtDM88hOTFLgLpZXu"
EMAIL = "mattia.millebolle@gmail.com"
PASSWORD = "Millebolle.1"
REGION = "eu"

url = "https://eu-api.coolkit.cc/v2/user/login"

headers = {
    "Content-Type": "application/json",
    "X-CK-Appid": APP_ID
}

payload = {
    "email": EMAIL,
    "password": PASSWORD,
    "countryCode": "39"
}

response = requests.post(url, json=payload, headers=headers)

print("STATUS:", response.status_code)
print("RESPONSE:")
print(response.text)
