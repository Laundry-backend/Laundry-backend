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
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except Exception as e:
        print("❌ Errore firma webhook:", e)
        return "", 400

    print("✅ Evento ricevuto:", event["type"])

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]

        # Recupero line items (serve per arrivare al prodotto)
        line_items = stripe.checkout.Session.list_line_items(
            session["id"],
            limit=1
        )

        item = line_items.data[0]
        price_id = item.price.id

        # Recupero il prodotto collegato
        price = stripe.Price.retrieve(price_id)
        product = stripe.Product.retrieve(price.product)

        print("🎯 PRODOTTO:", product.name)
        print("📦 METADATA:", product.metadata)

        # Qui userai product.metadata per decidere cosa fare
        # es: product.metadata["machine"]

    return "", 200



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

