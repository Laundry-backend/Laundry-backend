import os
import stripe
import logging
from flask import Flask, request

# ---------------------------------
# CONFIGURAZIONE LOGGING
# ---------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------
# CONFIG STRIPE
# ---------------------------------
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET")

# ---------------------------------
# CONFIG MACCHINE
# ---------------------------------
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

# ---------------------------------
# APP
# ---------------------------------
app = Flask(__name__)


@app.route("/")
def home():
    return "Backend lavanderia attivo"


# ---------------------------------
# WEBHOOK STRIPE
# ---------------------------------
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

    logger.info(f"📨 Ti
