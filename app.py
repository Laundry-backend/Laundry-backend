import os
import stripe
import logging
import threading
import time
from flask import Flask, request, render_template
from datetime import datetime
PULSE_ON_TIME = 1.0   # secondi ON e
PULSE_OFF_TIME = 1.0  # secondi OFF e

# -------------------------------------------------
# CONFIG
# -------------------------------------------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET")

# -------------------------------------------------
# TEMPO DI BLOCCO DOPO AVVIO
# -------------------------------------------------

# Tempo di blocco macchina (secondi)
LOCK_TIME = 180   # espresso in secondi

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
        "lavatrice_1_animali": {"impulses": 4},
        "lavatrice_3": {"impulses": 5},
        "lavatrice_4": {"impulses": 5},
        "lavatrice_5": {"impulses": 8},
        "lavatrice_6": {"impulses": 8},
        "asciugatrice_2_animali": {"impulses": 4},
        "asciugatrice_7": {"impulses": 5},
        "asciugatrice_8": {"impulses": 5},
    }
}

# -----------------------------
# STATO E LOCK DI SICUREZZA
# -----------------------------

machine_status = {
    loc: {
        name: {
            "status": "idle",
            "last_start": None
        } for name in machines
    } for loc, machines in MACHINES.items()
}
 
# Lock per evitare doppie attivazioni
machine_locks = {
    loc: {
        name: False for name in machines
    } for loc, machines in MACHINES.items()
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


@app.route("/webhook/stripe", methods=["POST"])
def stripe_webhook():
    payload = request.data
    sig = request.headers.get("Stripe-Signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig, STRIPE_WEBHOOK_SECRET
        )
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return "", 400

    if event["type"] != "checkout.session.completed":
        return "", 200

    session = event["data"]["object"]
    line_items = stripe.checkout.Session.list_line_items(session["id"], limit=1)
    item = line_items.data[0]
    price = stripe.Price.retrieve(item.price.id)
    product = stripe.Product.retrieve(price.product)

    machine = product.metadata.get("machine")
    location = product.metadata.get("location")

    if not machine or not location:
        return "", 400

    # sicurezza
    if location not in MACHINES or machine not in MACHINES[location]:
        return "", 400

    # EVITA DOPPIO AVVIO
    if machine_status[location][machine]["status"] == "running":
        logger.warning(f"⚠️ Tentativo doppio avvio: {machine}")
        return "", 200
    # BLOCCO SE GIÀ IN USO
    if machine_locks[location][machine]:
        logger.warning(f"⛔ Macchina {machine} già in funzione")
        return "", 200

    # Segna come occupata
    def worker():
        logger.info(f"🚀 Avvio macchina {machine}")
        
        # MACCHINA IN FUNZIONE
        machine_status[location][machine]["status"] = "running"
        machine_status[location][machine]["last_start"] = datetime.now().isoformat()

        # ---- IMPULSI ----
        for i in range(MACHINES[location][machine]["impulses"]):
            logger.info(f"⚡ Impulso {i+1}/{MACHINES[location][machine]['impulses']} - ON")
            time.sleep(PULSE_ON_TIME)

            logger.info(f"⚡ Impulso {i+1}/{MACHINES[location][machine]['impulses']} - OFF")
            time.sleep(PULSE_OFF_TIME)
  
        # BLOCCO MACCHINA (lavaggio in corso)
        machine_status[location][machine]["status"] = "in uso"
        logger.info(f"⏳ Macchina bloccata per {LOCK_TIME} secondi")
        time.sleep(LOCK_TIME)
        
        # RITORNA PRONTA A RICEVERE PAGAMENTO
        machine_status[location][machine]["status"] = "pronta a ricevere pagamento"
        logger.info(f"✅ Macchina {machine} pronta")
    
    threading.Thread(target=worker, daemon=True).start()

    return "", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
