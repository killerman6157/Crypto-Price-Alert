import os
import json
import logging

logger = logging.getLogger(__name__)
ALERTS_FILE = "alerts.json"

def load_alerts():
    """Loads alerts from the JSON file."""
    if os.path.exists(ALERTS_FILE):
        with open(ALERTS_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                logger.warning("⚠️ alerts.json is empty or malformed. Initializing as empty dict.")
                return {}
    return {}

def save_alerts(data):
    """Saves alerts to the JSON file."""
    try:
        with open(ALERTS_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        logger.error(f"❌ Failed to save alerts: {e}")
