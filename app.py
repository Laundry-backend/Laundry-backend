import os
import stripe
import logging
import requests
from flask import Flask, request, render_template
from datetime import datetime

# -------------------------------------------------
# CONFIG
# -------------------------------------------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET")

# IP della VM Home Assistant (solo LAN)
HOME_ASSISTANT_URL = "http://10.220.89.34:8123"

# -------------------------------------------------
# CONFIGURAZIONE MACCHINE (SEDE VERUCCHIO)
# -------------------------------------------------
MACHINES = {
    "lavatrice_1_animali": {"impulses": 4},
    "lavatrice_3": {"impulses": 5},
    "lavatrice_4": {"impulses": 5},
    "lavatrice_5": {"impulses": 8},
    "lavatrice_6": {"impulses": 8},
    "asciugatrice_2_animali": {"impulses": 4},
    "asciugatrice_7": {"impulses": 5},
    "asciugatrice_8": {"impulses": 5},
}

# -------------------------------------------------
# STATO E LOCK DI SICUREZZA
# -------------------------------------------------
machine_status = {
    name: {
        "status": "idle",
        "last_start": None
    } for name in MACHINES
}

# -------------------------------------------------
# APP
# -------------------------------------------------
app = Flask(__name__)

@app.route("/")
def home():
    return render_template("dashboard.html", machines=machine_status)

@app.route("/status")
def status():
    return machine_status

# -------------------------------------------------
# HOME ASSISTANT WEBHOOK
# -------------------------------------------------
def trigger_home_assistant(machine: str):
    url = f"{HOME_ASSISTANT_URL}/api/webhook/{machine}"
    try:
        r = requests.post(url, timeout=3)
        r.raise_for_status()
        logger.info(f"✅ Webhook HA inviato per {machine}")
    except Exception as e:
        logger.error(f"❌ Errore webhook HA ({machine}): {e}")

# -------------------------------------------------
# STRIPE WEBHOOK
# -------------------------------------------------
@app.route("/webhook/stripe", methods=["POST"])
def stripe_webhook():
    payload = request.data
    sig = request.headers.get("Stripe-Signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig, STRIPE_WEBHOOK_SECRET
        )
    except Exception as e:
        logger.error(f"❌ Errore firma Stripe: {e}")
        return "", 400

    # ascoltiamo solo pagamenti completati
    if event["type"] != "checkout.session.completed":
        return "", 200

    session = event["data"]["object"]

    try:
        line_items = stripe.checkout.Session.list_line_items(
            session["id"], limit=1
        )
        item = line_items.data[0]
        price = stripe.Price.retrieve(item.price.id)
        product = stripe.Product.retrieve(price.product)
    except Exception as e:
        logger.error(f"❌ Errore recupero prodotto Stripe: {e}")
        return "", 400

    # METADATA STRIPE
    machine = product.metadata.get("machine")

    if not machine or machine not in MACHINES:
        logger.error(f"❌ Macchina non valida: {machine}")
        return "", 400

    # EVITA DOPPIO AVVIO
    if machine_status[machine]["status"] != "idle":
        logger.warning(f"⛔ Macchina {machine} già in uso")
        return "", 200

    # SEGNA AVVIO
    machine_status[machine]["status"] = "running"
    machine_status[machine]["last_start"] = datetime.now().isoformat()

    logger.info(f"🚀 Avvio autorizzato per {machine}")

    # CHIAMA HOME ASSISTANT
    trigger_home_assistant(machine)

    return "", 200

# -------------------------------------------------
# MAIN
# -------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
