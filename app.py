import os
import stripe
import logging
import threading
import time
from flask import Flask, request, render_template
from datetime import datetime

# -------------------------------------------------
# LOG
# -------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -------------------------------------------------
# STRIPE
# -------------------------------------------------
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET")

# -------------------------------------------------
# CONFIG
# -------------------------------------------------
MACHINES = {
    "gambettola": {
        "lavatrice_1": {"impulses": 1},
        "lavatrice_2": {"impulses": 1},
    }
}

# Stato macchine
machine_status = {
    loc: {k: {"status": "idle", "last_start": None} for k in v}
    for loc, v in MACHINES.items()
}

# -------------------------------------------------
# APP
# -------------------------------------------------
app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html", machines=machine_status)

@app.route("/status")
def status():
    return machine_status

@app.route("/webhook/stripe", methods=["POST"])
def stripe_webhook():
    payload = request.data
    sig = request.headers.get("Stripe-Signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig, STRIPE_WEBHOOK_SECRET
        )
    except Exception:
        return "", 400

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        product = stripe.Product.retrieve(
            stripe.Price.retrieve(
                session["line_items"]["data"][0]["price"]
            ).product
        )

        machine = product.metadata.get("machine")
        location = product.metadata.get("location")

        if not machine or not location:
            return "", 400

        def run():
            machine_status[location][machine]["status"] = "running"
            time.sleep(2)
            machine_status[location][machine]["status"] = "idle"

        threading.Thread(target=run, daemon=True).start()

    return "", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
