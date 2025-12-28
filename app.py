import os
import stripe
import logging
from flask import Flask, request

# -------------------------------------------------
# CONFIGURAZIONE LOG
# -------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# -------------------------------------------------
# CONFIG STRIPE
# -------------------------------------------------
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET")

# -------------------------------------------------
# CONFIG MACCHINE
# -------------------------------------------------
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

# -------------------------------------------------
# APP
# -------------------------------------------------
app = Flask(__name__)


@app.route("/")
def home():
    return "Backend lavanderia attivo"


# -------------------------------------------------
# WEBHOOK STRIPE
# -------------------------------------------------
@app.route("/webhook/stripe", methods=["POST"])
def stripe_webhook():
    logger.info("📥 Webhook ricevuto")

    payload = request.data
    sig_header = request.headers.get("Stripe-Signature")

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            STRIPE_WEBHOOK_SECRET
        )
        logger.info("✅ Evento verificato")
    except Exception as e:
        logger.error(f"❌ Errore verifica webhook: {e}")
        return "", 400

    logger.info(f"📨 Tipo evento: {event['type']}")

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]

        # Recupera il prodotto acquistato
        line_items = stripe.checkout.Session.list_line_items(
            session["id"],
            limit=1
        )

        item = line_items.data[0]
        price = stripe.Price.retrieve(item.price.id)
        product = stripe.Product.retrieve(price.product)

        logger.info(f"💰 PAGAMENTO COMPLETATO")
        logger.info(f"📦 PRODOTTO: {product.name}")
        logger.info(f"📦 METADATA: {product.metadata}")

        # Qui in futuro:
        # attiva_macchina(product.metadata)

    return "", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
