import requests
import json
import re
import sys
import time
import os

print("--- 🏭 STARTING FACTORY (DIRECT KEY MODE) ---")

# 👇👇👇 YAHAN APNI KEY PASTE KAR (Double quotes ke andar) 👇👇👇
API_KEY = "AIzaSyBttt7j1uFig01pysOf2gv9G2_URJufmvw"
# 👆👆👆👆👆👆👆👆👆👆👆👆👆👆👆👆👆👆👆👆👆👆👆👆

if "YAHAN_APNI" in API_KEY:
    print("❌ ABE! Key to paste kar line 11 pe!")
    sys.exit(1)

INVENTORY_FILE = "inventory.txt"

# --- 1. CONNECT ---
def generate(prompt):
    # Hum seedha URL use kar rahe hain, library nahi. Ye kabhi fail nahi hota.
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    headers = {'Content-Type': 'application/json'}
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        if response.status_code == 200:
            return response.json()
        else:
            print(f"⚠️ Google Error {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return None

# --- 2. MEMORY ---
current_inventory = []
if os.path.exists(INVENTORY_FILE):
    with open(INVENTORY_FILE, "r") as f:
        current_inventory = [line.strip() for line in f.readlines() if line.strip()]

# --- 3. RESEARCH ---
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
if not data:
    print("❌ Research failed. Key check kar bhai.")
    sys.exit(1)

try:
    new_product_idea = data['candidates'][0]['content']['parts'][0]['text'].strip()
    new_product_idea = re.sub(r'[^a-zA-Z0-9_ ]', '', new_product_idea)
    print(f"💡 IDEA: {new_product_idea}")
except:
    print("❌ Google ne response diya par format galat tha.")
    sys.exit(1)

# --- 4. BUILD ---
print(f"🛠️ Building HTML for {new_product_idea}...")
design_prompt = f"""
Write HTML for "{new_product_idea}".
Theme: #121212 Dark Mode.
Feature: Editable content, Print to PDF.
Return ONLY raw HTML.
"""

time.sleep(1)
data = generate(design_prompt)

if data:
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

