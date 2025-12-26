from flask import Flask, request

app = Flask(__name__)

@app.route("/webhook/stripe", methods=["POST"])
def stripe_webhook():
    print("Webhook Stripe ricevuto")
    return "OK", 200

@app.route("/")
def home():
    return "Backend lavanderia attivo"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
