
import requests
import json
import os
import re
import sys
import time

print("--- 🏭 STARTING FACTORY (MACHINE GUN MODE) ---")

if "API_KEY" not in os.environ:
    print("❌ FATAL: API_KEY not found!")
    sys.exit(1)

API_KEY = os.environ["API_KEY"]
INVENTORY_FILE = "inventory.txt"

# --- STRATEGY: Try Every Combination ---
# Google ke alag-alag versions aur model names
VERSIONS = ["v1beta", "v1"]
MODELS = [
    "gemini-1.5-flash-latest", # Aksar ye chalta hai
    "gemini-1.5-flash",        # Standard
    "gemini-1.5-flash-002",    # New Stable
    "gemini-1.5-flash-001",    # Old Stable
    "gemini-1.5-pro",
    "gemini-pro",
    "gemini-2.0-flash-exp"     # Experimental
]

def try_generate(prompt, model, version):
    url = f"https://generativelanguage.googleapis.com/{version}/models/{model}:generateContent?key={API_KEY}"
    headers = {'Content-Type': 'application/json'}
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

# 1. FIND WORKING COMBO
working_config = None
print(f"🔍 Testing Connections...")

found = False
for ver in VERSIONS:
    if found: break
    for mod in MODELS:
        print(f"👉 Trying: {mod} on {ver}...")
        res = try_generate("Say Hi", mod, ver)
        if res and 'candidates' in res:
            working_config = (mod, ver)
            print(f"✅ SUCCESS! Connected via: {mod} ({ver})")
            found = True
            break
        time.sleep(0.5) # Thoda saans lene do

if not working_config:
    print("❌ FATAL: Sab fail ho gaya. API Key check karo ya Nayi Key banao.")
    sys.exit(1)

ACTIVE_MODEL, ACTIVE_VERSION = working_config

# 2. MEMORY
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

data = try_generate(research_prompt, ACTIVE_MODEL, ACTIVE_VERSION)
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
data = try_generate(design_prompt, ACTIVE_MODEL, ACTIVE_VERSION)

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
