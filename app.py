import os
import stripe
import logging
import threading
import time
from flask import Flask, request, render_template
from datetime import datetime

# -------------------------------------------------
# CONFIGURAZIONE LOG
# -------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# -------------------------------------------------
# STRIPE
# -------------------------------------------------
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET")

# -------------------------------------------------
# CONFIGURAZIONE MACCHINE
# -------------------------------------------------
MACHINES = {
    "gambettola": {
        "lavatrice_1": {"impulses": 1},
        "lavatrice_2": {"impulses": 1},
        "lavatrice_3": {"impulses": 1},
        "lavatrice_4": {"impulses": 1},
        "lavatrice_5": {"impulses": 1},
        "lavatrice_6": {"impulses": 1},
        "lavatrice_7": {"impulses": 1},
        "asciugatrice_8": {"impulses": 1},
        "asciugatrice_9": {"impulses": 1},
        "asciugatrice_10": {"impulses": 1},
        "asciugatrice_11": {"impulses": 1},
        "asciugatrice_12": {"impulses": 1},
    },
    "verucchio": {
        "lavatrice_1": {"impulses": 4},
        "lavatrice_3": {"impulses": 5},
        "lavatrice_4": {"impulses": 5},
        "lavatrice_5": {"impulses": 8},
        "lavatrice_6": {"impulses": 8},
        "asciugatrice_2": {"impulses": 4},
        "asciugatrice_7": {"impulses": 5},
        "asciugatrice_8": {"impulses": 5},
    }
}

# -------------------------------------------------
# STATO MACCHINE
# -------------------------------------------------
machine_status = {
    location: {
        name: {"status": "idle", "last_start": None}
        for name in machines
    }
    for location, machines in MACHINES.items()
}

# -------------------------------------------------
# FLASK APP
# -------------------------------------------------
app = Flask(__name__)

# -------------------------------------------------
# ROUTES
# -------------------------------------------------

@app.route("/")
def home():
    return render_template("index.html", machines=machine_status)


@app.route("/status")
def status():
    return machine_status


@app.route("/webhook/stripe", methods=["POST"])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return "", 400

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]

        line_items = stripe.checkout.Session.list_line_items(session["id"], limit=1)
        item = line_items.data[0]
        price = stripe.Price.retrieve(item.price.id)
        product = stripe.Product.retrieve(price.product)

        machine = product.metadata.get("machine")
        location = product.metadata.get("location")

        if not machine or not location:
            return "", 400

        if location not in MACHINES or machine not in MACHINES[location]:
            return "", 400

        def worker():
            machine_status[location][machine]["status"] = "running"
            machine_status[location][machine]["last_start"] = datetime.now().isoformat()
            time.sleep(MACHINES[location][machine]["impulses"])
            machine_status[location][machine]["status"] = "idle"

        threading.Thread(target=worker, daemon=True).start()

    return "", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
