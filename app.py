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
    app.logger.info("📥 Webhook ricevuto")

    payload = request.data
    app.logger.info(f"📦 RAW PAYLOAD: {payload}")

    sig_header = request.headers.get("Stripe-Signature")
    app.logger.info(f"🔐 Signature: {sig_header}")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
        app.logger.info("✅ Evento verificato")
    except Exception as e:
        app.logger.error(f"❌ Errore verifica webhook: {e}")
        return "", 400

    app.logger.info(f"📨 Tipo evento: {event['type']}")

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        app.logger.info(f"💰 PAGAMENTO COMPLETATO")
        app.logger.info(f"👉 Metadata: {session.get('metadata')}")

    return "", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

