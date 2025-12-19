import requests
import json
import os
import re
import sys
import time

print("--- 🏭 STARTING FACTORY (RAW REQUEST MODE) ---")

if "API_KEY" not in os.environ:
    print("❌ FATAL: API_KEY not found!")
    sys.exit(1)

API_KEY = os.environ["API_KEY"]
INVENTORY_FILE = "inventory.txt"

# Hum in models ko try karenge. Jo chalega usse pakad lenge.
MODELS = [
    "gemini-1.5-flash",
    "gemini-1.5-pro",
    "gemini-2.0-flash-exp",
    "gemini-1.5-flash-latest"
]

def generate_content(prompt, model_name):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={API_KEY}"
    headers = {'Content-Type': 'application/json'}
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

# 1. FIND WORKING MODEL
working_model = None
print("🔍 Checking Google Brain...")

for m in MODELS:
    test = generate_content("Say Hi", m)
    if test and 'candidates' in test:
        working_model = m
        print(f"✅ LOCKED ON: {m}")
        break
    else:
        print(f"⚠️ {m} Failed. Trying next...")

if not working_model:
    print("❌ ALL MODELS FAILED. Check API Key.")
    sys.exit(1)

# 2. READ MEMORY
current_inventory = []
if os.path.exists(INVENTORY_FILE):
    with open(INVENTORY_FILE, "r") as f:
        current_inventory = [line.strip() for line in f.readlines() if line.strip()]

# 3. RESEARCH
print("🧠 Researching Market Gaps...")
research_prompt = f"""
Act as a Product Researcher.
Current Inventory: {current_inventory}.
Find 1 High-Ticket B2B HTML Document missing from list.
Target: US Agencies.
Name format: Clean, Simple, Professional. No special chars.
Return ONLY the Name.
"""

data = generate_content(research_prompt, working_model)
if not data:
    print("❌ Research Failed.")
    sys.exit(1)

new_product_idea = data['candidates'][0]['content']['parts'][0]['text'].strip()
new_product_idea = re.sub(r'[^a-zA-Z0-9_ ]', '', new_product_idea)
print(f"💡 SELECTED PRODUCT: {new_product_idea}")

# 4. BUILD
print(f"🛠️ Building HTML...")
design_prompt = f"""
Write HTML for "{new_product_idea}".
Theme: #121212 Dark Mode.
Feature: <span contenteditable="true"> for text.
Feature: Print to PDF button.
Return ONLY raw HTML.
"""

time.sleep(1)
data = generate_content(design_prompt, working_model)

if not data:
    print("❌ Build Failed.")
    sys.exit(1)

html_code = data['candidates'][0]['content']['parts'][0]['text']
html_code = html_code.replace("```html", "").replace("```", "")

filename = f"{new_product_idea.replace(' ', '_')}.html"

with open(filename, "w") as f:
    f.write(html_code)

with open(INVENTORY_FILE, "a") as f:
    f.write(f"\n{new_product_idea}")

print(f"\n✅ SUCCESS: Created {filename}")

