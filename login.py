import requests
import json

APP_ID = "0ygkstU1AovdDXtI65mok181GCCY87EF"
APP_SECRET = "0UZMVs2oaSoFiYcqtDM88hOTFLgLpZXu"
EMAIL = "mattia.millebolle@gmail.com"
PASSWORD = "Millebolle.1"

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

r = requests.post(url, headers=headers, json=payload)

print("STATUS:", r.status_code)
print("RESPONSE:", r.text)
