import json
import os

ALERTS_FILE = "alerts.json"

def load_alerts():
    if os.path.exists(ALERTS_FILE):
        with open(ALERTS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_alerts(alerts):
    with open(ALERTS_FILE, "w") as f:
        json.dump(alerts, f, indent=2)

price_alerts = load_alerts()  # Load alerts at import time
