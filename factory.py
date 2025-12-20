import requests
import json
import re
import sys
import time
import os

print("--- 🏭 STARTING FACTORY (MULTI-MODEL HARDCODED) ---")

# 👇👇👇 PASTE YOUR KEY HERE 👇👇👇
API_KEY = "AIzaSyBttt7j1uFig01pysOf2gv9G2_URJufmvw"
# 👆👆👆👆👆👆👆👆👆👆👆👆👆👆👆👆

if "YAHAN" in API_KEY:
    print("❌ ERROR: Bhai Key paste karna bhul gaya code mein!")
    sys.exit(1)

INVENTORY_FILE = "inventory.txt"

# --- STRATEGY: TRY ALL DOORS ---
# Google ke alag alag model names
POSSIBLE_MODELS = [
    "gemini-1.5-flash",
    "gemini-1.5-flash-latest",
    "gemini-pro",              # Sabse purana aur reliable
    "gemini-1.5-pro-latest",
    "gemini-1.0-pro"
]

WORKING_URL = None

print("🔍 Finding a working Model...")

for model in POSSIBLE_MODELS:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={API_KEY}"
    headers = {'Content-Type': 'application/json'}
    # Test Payload
    payload = {"contents": [{"parts": [{"text": "Hi"}]}]}
    
    try:
        print(f"👉 Testing {model}...")
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        
        if response.status_code == 200:
            print(f"✅ BINGO! Connected to: {model}")
            WORKING_URL = url
            break
        else:
            print(f"⚠️ {model} Failed ({response.status_code})...")
    except:
        continue

if not WORKING_URL:
    print("❌ FATAL: Saare models fail ho gaye. Shayad Google API Issue hai.")
    sys.exit(1)

# --- FUNCTION TO GENERATE ---
def generate(prompt):
    headers = {'Content-Type': 'application/json'}
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        r = requests.post(WORKING_URL, headers=headers, data=json.dumps(payload))
        return r.json()
    except:
        return None

# --- 1. MEMORY ---
current_inventory = []
if os.path.exists(INVENTORY_FILE):
    with open(INVENTORY_FILE, "r") as f:
        current_inventory = [line.strip() for line in f.readlines() if line.strip()]

# --- 2. RESEARCH ---
print("🧠 Researching...")
research_prompt = f"""
Act as a Product Researcher.
Current Inventory: {current_inventory}.
Find 1 High-Ticket B2B HTML Document missing from list.
Target: US Agencies.
Name format: Clean, Simple, Professional. No special chars.
Return ONLY the Name.
"""

data = generate(research_prompt)
if not data or 'candidates' not in data:
    print("❌ Research failed.")
    sys.exit(1)

new_product_idea = data['candidates'][0]['content']['parts'][0]['text'].strip()
new_product_idea = re.sub(r'[^a-zA-Z0-9_ ]', '', new_product_idea)
print(f"💡 IDEA: {new_product_idea}")

# --- 3. BUILD ---
print(f"🛠️ Building HTML...")
design_prompt = f"""
Write HTML for "{new_product_idea}".
Theme: #121212 Dark Mode.
Feature: Editable content, Print to PDF.
Return ONLY raw HTML.
"""

time.sleep(1)
data = generate(design_prompt)

if data and 'candidates' in data:
    html_code = data['candidates'][0]['content']['parts'][0]['text']
    html_code = html_code.replace("```html", "").replace("```", "")
    
    filename = f"{new_product_idea.replace(' ', '_')}.html"
    
    with open(filename, "w") as f:
        f.write(html_code)

    with open(INVENTORY_FILE, "a") as f:
        f.write(f"\n{new_product_idea}")

    print(f"\n✅ SUCCESS: Created {filename}")
else:
    print("❌ HTML Generation failed.")
    sys.exit(1)

