# utils.py
import math
import re
import time
import json
from datetime import datetime

def now_ts():
    return datetime.now().isoformat()

def haversine_km(lat1, lon1, lat2, lon2):
    # returns distance in kilometers between two lat/lon points
    R = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def deidentify_text(text):
    # Very simple PII redaction for demo: redact numbers that look like phone/ID
    if not text:
        return text
    # remove emails
    text = re.sub(r'[\w\.-]+@[\w\.-]+\.\w+', '[REDACTED_EMAIL]', text)
    # remove phone numbers (simple)
    text = re.sub(r'\b\d{10}\b', '[REDACTED_PHONE]', text)
    # remove sequences of digits (IDs)
    text = re.sub(r'\b\d{4,}\b', '[REDACTED_ID]', text)
    return text

class EventLog:
    def __init__(self):
        self.events = []

    def log(self, source, message, data=None):
        e = {
            "ts": now_ts(),
            "source": source,
            "message": message,
            "data": data
        }
        self.events.append(e)
        print(f"[{e['ts']}] {source}: {message}")

    def to_list(self):
        return self.events

    def to_json(self):
        return json.dumps(self.events, indent=2)