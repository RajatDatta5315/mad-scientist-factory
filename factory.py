
import requests
import json
import os
import re
import sys
import time

print("--- 🏭 STARTING FACTORY (DEBUG MODE) ---")

if "API_KEY" not in os.environ:
    print("❌ FATAL: API_KEY not found! Secrets check karo.")
    sys.exit(1)

API_KEY = os.environ["API_KEY"]
INVENTORY_FILE = "inventory.txt"

# Models List
MODELS = [
    "gemini-1.5-flash",
    "gemini-1.5-pro",
    "gemini-pro"
]

def generate_content(prompt, model_name):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={API_KEY}"
    headers = {'Content-Type': 'application/json'}
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        if response.status_code == 200:
            return response.json()
        else:
            # --- YAHAN HAI MAGIC: Error print karo ---
            print(f"⚠️ {model_name} Error {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print(f"⚠️ Connection Failed: {e}")
        return None

# 1. FIND WORKING MODEL
working_model = None
print(f"🔍 Checking Google Brain using Key ending in ...{API_KEY[-4:]}")

for m in MODELS:
    print(f"👉 Testing {m}...")
    test = generate_content("Say Hi", m)
    if test and 'candidates' in test:
        working_model = m
        print(f"✅ LOCKED ON: {m}")
        break
    else:
        print(f"❌ {m} Failed.")

if not working_model:
    print("❌ FATAL: Sab models fail ho gaye. Upar wala Error message padho.")
    sys.exit(1)

# ... (Baaki code run karne ki zarurat nahi agar connection hi fail hai) ...
print("✅ Connection Successful! (Ab hum product bana sakte hain)")
