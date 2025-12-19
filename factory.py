import requests
import json
import os
import re
import sys
import time

# --- 1. SETUP ---
print("--- 🏭 STARTING FACTORY (MULTI-MODEL MODE) ---")

if "API_KEY" not in os.environ:
    print("❌ FATAL: API_KEY not found!")
    sys.exit(1)

API_KEY = os.environ["API_KEY"]
INVENTORY_FILE = "inventory.txt"

# --- 2. THE MODEL HOPPER (Smart Connection) ---
# Hum in sabko bari-bari try karenge
MODELS_TO_TRY = [
    "models/gemini-1.5-flash",
    "models/gemini-1.5-flash-latest",
    "models/gemini-1.5-pro",
    "models/gemini-1.0-pro",
    "models/gemini-pro"
]

WORKING_MODEL = None

print("🔍 Finding a working Brain...")

for model in MODELS_TO_TRY:
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/{model}?key={API_KEY}"
        # Test Call
        response = requests.get(url)
        if response.status_code == 200:
            WORKING_MODEL = model
            print(f"✅ LOCKED ON: {WORKING_MODEL}")
            break
        else:
            print(f"⚠️ {model} failed (Status: {response.status_code}). Trying next...")
    except:
        continue

if not WORKING_MODEL:
    print("❌ ALL MODELS FAILED. Google API Issue.")
    sys.exit(1)

# --- 3. MEMORY ---
current_inventory = []
if os.path.exists(INVENTORY_FILE):
    with open(INVENTORY_FILE, "r") as f:
        current_inventory = [line.strip() for line in f.readlines() if line.strip()]

# --- 4. RESEARCH ---
print("🧠 Researching Market Gaps...")
research_prompt = f"""
Act as a Product Researcher.
Current Inventory: {current_inventory}.
Find 1 High-Ticket B2B HTML Document missing from list.
Target: US Agencies.
Name format: Clean, Simple, Professional. No special chars.
Return ONLY the Name.
"""

url = f"https://generativelanguage.googleapis.com/v1beta/{WORKING_MODEL}:generateContent?key={API_KEY}"
headers = {'Content-Type': 'application/json'}
payload = {"contents": [{"parts": [{"text": research_prompt}]}]}

try:
    r = requests.post(url, headers=headers, data=json.dumps(payload))
    if r.status_code != 200:
        # Fallback for 2.5/Experimental issues
        print(f"❌ Research Error: {r.text}")
        sys.exit(1)
        
    data = r.json()
    if 'candidates' not in data:
         print("❌ Brain refused to give Idea.")
         sys.exit(1)

    new_product_idea = data['candidates'][0]['content']['parts'][0]['text'].strip()
    new_product_idea = re.sub(r'[^a-zA-Z0-9_ ]', '', new_product_idea)
    print(f"💡 SELECTED PRODUCT: {new_product_idea}")
    
except Exception as e:
    print(f"❌ Research Failed: {e}")
    sys.exit(1)

# --- 5. BUILD ---
print(f"🛠️ Building HTML...")
design_prompt = f"""
Write HTML for "{new_product_idea}".
Theme: #121212 Dark Mode.
Feature: <span contenteditable="true"> for text.
Feature: Print to PDF button.
Return ONLY raw HTML.
"""

payload = {"contents": [{"parts": [{"text": design_prompt}]}]}
time.sleep(1) 
r = requests.post(url, headers=headers, data=json.dumps(payload))

try:
    response_json = r.json()
    if 'candidates' not in response_json:
        print(f"❌ Code Generation Failed. Response: {response_json}")
        sys.exit(1)

    html_code = response_json['candidates'][0]['content']['parts'][0]['text']
    html_code = html_code.replace("```html", "").replace("```", "")
    
    filename = f"{new_product_idea.replace(' ', '_')}.html"
    
    with open(filename, "w") as f:
        f.write(html_code)

    with open(INVENTORY_FILE, "a") as f:
        f.write(f"\n{new_product_idea}")

    print(f"\n✅ SUCCESS: Created {filename}")

except Exception as e:
    print(f"❌ Build Failed: {e}")
    sys.exit(1)

