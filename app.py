import os
import stripe
import logging
from flask import Flask, request

# ----------------------------------------
# CONFIG LOGGING
# ----------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# ----------------------------------------
# STRIPE CONFIG
# ----------------------------------------
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET")

# ----------------------------------------
# CONFIG MACCHINE
# ----------------------------------------
MACHINES = {
    "gambettola": {
        "lavatrice_1": {"impulses": 1, "descrizione": "Lavatrice 8kg"},
        "lavatrice_2": {"impulses": 1, "descrizione": "Lavatrice 8kg"},
        "lavatrice_3": {"impulses": 1, "descrizione": "Lavatrice 8kg"},
        "lavatrice_4": {"impulses": 1, "descrizione": "Lavatrice 8kg"},
        "lavatrice_5": {"impulses": 1, "descrizione": "Lavatrice 18kg"},
        "lavatrice_6": {"impulses": 1, "descrizione": "Lavatrice 18kg"},
        "lavatrice_7": {"impulses": 1, "descrizione": "Lavatrice 18kg"},
        "asciugatrice_8": {"impulses": 1, "descrizione": "Asciugatrice"},
        "asciugatrice_9": {"impulses": 1, "descrizione": "Asciugatrice"},
        "asciugatrice_10": {"impulses": 1, "descrizione": "Asciugatrice"},
        "asciugatrice_11": {"impulses": 1, "descrizione": "Asciugatrice"},
        "asciugatrice_12": {"impulses": 1, "descrizione": "Asciugatrice"},
    },
    "verucchio": {
        "lavatrice_1": {"impulses": 5, "descrizione": "Lavatrice animali"},
        "lavatrice_3": {"impulses": 5, "descrizione": "Lavatrice 8kg"},
        "lavatrice_4": {"impulses": 5, "descrizione": "Lavatrice 8kg"},
        "lavatrice_5": {"impulses": 8, "descrizione": "Lavatrice 18kg"},
        "lavatrice_6": {"impulses": 8, "descrizione": "Lavatrice 18kg"},
        "asciugatrice_7": {"impulses": 5, "descrizione": "Asciugatrice"},
        "asciugatrice_8": {"impulses": 5, "descrizione": "Asciugatrice"},
    }
}

# ----------------------------------------
# APP
# ----------------------------------------
app = Flask(__name__)


@app.route("/")
def home():
    return "Backend lavanderia attivo"


@app.route("/webhook/stripe", methods=["POST"])
def stripe_webhook():
    logger.info("📥 Webhook ricevuto")

    payload = request.data
    sig_header = request.headers.get("Stripe-Signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
        logger.info("✅ Evento verificato")
    except Exception as e:
        logger.error(f"❌ Errore verifica webhook: {e}")
        return "", 400

    logger.info(f"📨 Tipo evento: {event['type']}")

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]

        # Recupero dati dal pagamento
        line_items = stripe.checkout.Session.list_line_items(
            session["id"],
            limit=1
        )

        item = line_items.data[0]
        price = stripe.Price.retrieve(item.price.id)
        product = stripe.Product.retrieve(price.product)

        # Metadata
        machine = product.metadata.get("machine")
        location = product.metadata.get("location")

        # VALIDAZIONE
        if not machine or not location:
            logger.error("❌ Metadata mancanti")
            return "", 400

        if location not in MACHINES:
            logger.error(f"❌ Location non valida: {location}")
            return "", 400

        if machine not in MACHINES[location]:
            logger.error(f"❌ Macchina non trovata: {machine}")
            return "", 400

        impulses = MACHINES[location][machine]["impulses"]

        logger.info(f"📍 Location: {location}")
        logger.info(f"⚙️ Macchina: {machine}")
        logger.info(f"🔁 Impulsi: {impulses}")

        # QUI andrà il comando reale per attivare il relè

    return "", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
