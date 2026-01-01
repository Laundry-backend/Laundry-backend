from flask import Flask, request
import requests

app = Flask(__name__)

APP_ID = "0ygkstU1AovdDXtI65mok181GCCY87EF"
APP_SECRET = "0UZMVs2oaSoFiYcqtDM88hOTFLgLpZXu"
REDIRECT_URI = "http://localhost:5000/callback"

@app.route("/callback")
def callback():
    code = request.args.get("code")
    if not code:
        return "Errore: codice non ricevuto"

    token_url = "https://eu-api.coolkit.cc/v2/user/oauth/token"

    payload = {
        "grantType": "authorization_code",
        "code": code,
        "redirectUrl": REDIRECT_URI,
        "clientId": APP_ID,
        "clientSecret": APP_SECRET
    }

    r = requests.post(token_url, json=payload)
    return r.text

if __name__ == "__main__":
    app.run(port=5000)
