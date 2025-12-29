import os
import stripe
import logging
import threading
import time
from flask import Flask, request, jsonify
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

# -------------------------------------------------
# STATO MACCHINE (in RAM)
# -------------------------------------------------
machine_status = {}

for location, machines in MACHINES.items():
    machine_status[location] = {}
    for name in machines:
        machine_status[location][name] = {
            "status": "idle",
            "last_start": None
        }

# -------------------------------------------------
# FUNZIONE ASINCRONA
# -------------------------------------------------
def attiva_macchina_async(location, machine, impulses):
    def worker():
        machine_status[location][machine]["status"] = "running"
        machine_status[location][machine]["last_start"] = datetime.now().isoformat()

        logger.info(f"🚀 Avvio macchina {machine} ({location})")

        for i in range(impulses):
            logger.info(f"⚡ Impulso {i+1}/{impulses}")
            time.sleep(1)

        machine_status[location][machine]["status"] = "idle"
        logger.info(f"✅ Fine ciclo {machine}")

    threading.Thread(target=worker, daemon=True).start()


# -------------------------------------------------
# ROUTES
# -------------------------------------------------
app = Flask(__name__)


from flask import render_template

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/dashboard")
def dashboard():
    return render_template("index.html", machines=machine_status)

def home():
    return "Backend lavanderia attivo"
    from flask import render_template

@app.route("/dashboard")
def dashboard():
    return render_template("index.html")



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
        logger.error(f"❌ Errore webhook: {e}")
        return "", 400

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]

        line_items = stripe.checkout.Session.list_line_items(
            session["id"], limit=1
        )

        item = line_items.data[0]
        price = stripe.Price.retrieve(item.price.id)
        product = stripe.Product.retrieve(price.product)

        machine = product.metadata.get("machine")
        location = product.metadata.get("location")

        if not machine or not location:
            logger.error("❌ Metadata mancanti")
            return "", 400

        if location not in MACHINES or machine not in MACHINES[location]:
            logger.error("❌ Macchina non valida")
            return "", 400

        impulses = MACHINES[location][machine]["impulses"]

        logger.info(f"📍 Location: {location}")
        logger.info(f"⚙️ Macchina: {machine}")
        logger.info(f"🔁 Impulsi: {impulses}")

        attiva_macchina_async(location, machine, impulses)

    return "", 200

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
