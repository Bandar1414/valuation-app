# app/visitor_tracker.py

import json
import os
from flask import request

VISITORS_FILE = "visitors.json"

def load_visitors():
    if os.path.exists(VISITORS_FILE):
        with open(VISITORS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_visitors(data):
    with open(VISITORS_FILE, "w") as f:
        json.dump(data, f)

def count_unique_visitor():
    ip = request.remote_addr
    visitors = load_visitors()
    if ip not in visitors:
        visitors[ip] = True
        save_visitors(visitors)
