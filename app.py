import os
import stripe
from flask import Flask, request, jsonify, abort

app = Flask(__name__)

# Inserisci la tua secret key di Stripe come variabile d'ambiente
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET")

@app.route("/")
def home():
    return "Backend lavanderia attivo"

@app.route("/webhook/stripe", methods=["POST"])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature")

    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=sig_header,
            secret=STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return "Invalid payload", 400
    except stripe.error.SignatureVerificationError:
        return "Invalid signature", 400

    # Evento valido
    print("Evento ricevuto:", event["type"])

    if event["type"] == "checkout.session.completed":
        print("💰 Pagamento completato!")
        # Qui in futuro attiveremo il relè

    return "", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

