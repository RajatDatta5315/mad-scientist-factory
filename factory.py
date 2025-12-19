import requests
import json
import os
import re
import sys
import time

# --- 1. SETUP ---
print("--- 🏭 STARTING FACTORY (STABLE MODE) ---")

if "API_KEY" not in os.environ:
    print("❌ FATAL: API_KEY not found in secrets!")
    sys.exit(1)

API_KEY = os.environ["API_KEY"]
INVENTORY_FILE = "inventory.txt"

# --- 2. CONNECT (FORCE STABLE MODEL) ---
# Hum auto-detect nahi karenge, seedha 1.5 Flash use karenge jo fast aur stable hai
MY_MODEL = "models/gemini-1.5-flash"
print(f"🔒 Locked to Stable Model: {MY_MODEL}")

# --- 3. MEMORY ---
print(f"📖 Reading Diary...")
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

url = f"https://generativelanguage.googleapis.com/v1beta/{MY_MODEL}:generateContent?key={API_KEY}"
headers = {'Content-Type': 'application/json'}
payload = {"contents": [{"parts": [{"text": research_prompt}]}]}

try:
    r = requests.post(url, headers=headers, data=json.dumps(payload))
    if r.status_code != 200:
        print(f"❌ Research Error: {r.text}")
        sys.exit(1)
        
    data = r.json()
    new_product_idea = data['candidates'][0]['content']['parts'][0]['text'].strip()
    # Name Cleaning
    new_product_idea = re.sub(r'[^a-zA-Z0-9_ ]', '', new_product_idea)
    print(f"💡 SELECTED PRODUCT: {new_product_idea}")
    
except Exception as e:
    print(f"❌ Research Failed: {e}")
    sys.exit(1)

# --- 5. BUILD (HTML GENERATION) ---
print(f"🛠️ Building HTML...")
design_prompt = f"""
Write HTML for "{new_product_idea}".
Theme: #121212 Dark Mode.
Feature: <span contenteditable="true"> for text.
Feature: Print to PDF button.
Return ONLY raw HTML.
"""

payload = {"contents": [{"parts": [{"text": design_prompt}]}]}
# Thoda delay taaki Google block na kare
time.sleep(2) 
r = requests.post(url, headers=headers, data=json.dumps(payload))

try:
    if r.status_code != 200:
        print(f"❌ Build API Error: {r.text}")
        sys.exit(1)

    response_json = r.json()
    
    # DEBUGGING: Agar 'candidates' nahi aaya to error print karo
    if 'candidates' not in response_json:
        print(f"❌ GOOGLE REFUSED TO GENERATE CODE.")
        print(f"Full Response: {response_json}")
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
    print(f"❌ Code Generation Failed: {e}")
    sys.exit(1)

