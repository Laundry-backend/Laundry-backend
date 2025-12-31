import time
import hmac
import hashlib
import requests
import json

APP_ID = "
0ygkstU1AovdDXtI65mok181GCCY87EF"
APP_SECRET = "
0UZMVs2oaSoFiYcqtDM88hOTFLgLpZXu"

url = "https://eu-apia.coolkit.cc/v2/user/login"

timestamp = str(int(time.time() * 1000))
nonce = "123456"

payload = {
    "email": "mattia.millebolle@gmail.com",
    "password": "Millebolle.1",
    "countryCode": "39"
}

# genera firma
message = APP_ID + nonce + timestamp
sign = hmac.new(
    APP_SECRET.encode(),
    message.encode(),
    hashlib.sha256
).hexdigest()

headers = {
    "Content-Type": "application/json",
    "X-CK-Appid": APP_ID,
    "X-CK-Nonce": nonce,
    "Authorization": f"Sign {sign}",
    "X-CK-Expire": timestamp
}

res = requests.post(url, json=payload, headers=headers)
print(res.status_code)
print(res.text)
