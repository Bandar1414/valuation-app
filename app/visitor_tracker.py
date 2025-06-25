import json
import os
from flask import request
from datetime import datetime

TMP_DIR = 'tmp'
VISITORS_FILE = os.path.join(TMP_DIR, 'visitors.json')
os.makedirs(TMP_DIR, exist_ok=True)

def load_visitors():
    if os.path.exists(VISITORS_FILE):
        with open(VISITORS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "total_visits": 0,
        "ips": {}
    }

def save_visitors(data):
    with open(VISITORS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def count_unique_visitor():
    data = load_visitors()
    ip = request.remote_addr
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if ip not in data["ips"]:
        data["ips"][ip] = {
            "first_visit": now,
            "visits": 1,
            "last_visit": now
        }
    else:
        data["ips"][ip]["visits"] += 1
        data["ips"][ip]["last_visit"] = now

    data["total_visits"] += 1
    save_visitors(data)

def get_visitor_count():
    data = load_visitors()
    return len(data["ips"])

def get_total_visits():
    data = load_visitors()
    return data.get("total_visits", 0)

def get_all_visitors():
    data = load_visitors()
    return data["ips"]
