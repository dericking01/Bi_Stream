import json
import os
from datetime import datetime

STATE_FILE = "state.json"

def load_state():
    if not os.path.exists(STATE_FILE):
        return {}
    with open(STATE_FILE, "r") as f:
        return json.load(f)

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def get_last_execution(report_name):
    state = load_state()
    return state.get(report_name, "1970-01-01 00:00:00")

def update_last_execution(report_name):
    state = load_state()
    state[report_name] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_state(state)