import os
import stripe
from flask import Flask, request, jsonify

app = Flask(__name__)

# Chiavi Stripe
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET")

# Mappa macchine → logica di attivazione
MACHINES = {
    "gambettola": {
        "lavatrice_1": {
            "impulses": 1,
            "descrizione": "Lavatrice 8kg"
        },
        "asciugatrice_1": {
            "impulses": 2,
            "descrizione": "Asciugatrice 1"
        }
    },
    "verucchio": {
        "lavatrice_1": {
            "impulses": 3,
            "descrizione": "Lavatrice grande"
        }
    }
}
import time

def attiva_macchina(luogo, macchina):
    config = MACHINES.get(luogo, {}).get(macchina)

    if not config:
        print("❌ Macchina non trovata:", luogo, macchina)
        return

    impulsi = config["impulses"]

    print(f"▶️ Avvio {macchina} ({luogo}) - impulsi: {impulsi}")

    for i in range(impulsi):
        print(f"   Impulso {i+1}")
        time.sleep(1)

    print("✅ Ciclo completato")

@app.route("/")
def home():
    return "Backend lavanderia attivo"

@app.route("/webhook/stripe", methods=["POST"])
def stripe_webhook():
    print("📥 Webhook ricevuto")

    payload = request.data
    print("📦 RAW PAYLOAD:")
    print(payload)

    sig_header = request.headers.get("Stripe-Signature")
    print("🔐 Signature:", sig_header)

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
        print("✅ Evento verificato")
    except Exception as e:
        print("❌ Errore verifica webhook:", str(e))
        return "", 400

    print("📨 Tipo evento:", event["type"])

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        print("💰 PAGAMENTO COMPLETATO")
        print("👉 Metadata:", session.get("metadata"))

    return "", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

