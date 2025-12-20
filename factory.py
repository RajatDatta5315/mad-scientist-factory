import requests
import json
import re
import sys
import time
import os

print("--- 🏭 STARTING FACTORY (UNIVERSAL SEARCH MODE) ---")

# 👇👇👇 PASTE KEY HERE 👇👇👇
API_KEY = "AIzaSyBttt7j1uFig01pysOf2gv9G2_URJufmvw"
# 👆👆👆👆👆👆👆👆👆👆👆👆👆👆

if "YAHAN" in API_KEY:
    print("❌ ERROR: Bhai Key paste karna bhul gaya!")
    sys.exit(1)

INVENTORY_FILE = "inventory.txt"

# --- STEP 1: ASK GOOGLE "WHAT DO YOU HAVE?" ---
print("🔍 Scanning Google Server for ANY working model...")

# Hum list mangenge
list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"
WORKING_MODEL = None
WORKING_VERSION = "v1beta"

try:
    response = requests.get(list_url)
    if response.status_code == 200:
        data = response.json()
        # List mein se dhundo kaunsa model text generate kar sakta hai
        if 'models' in data:
            for m in data['models']:
                name = m['name'] # e.g. models/gemini-1.5-flash
                methods = m.get('supportedGenerationMethods', [])
                
                if 'generateContent' in methods:
                    # Test karo ki ye chalta hai ya nahi
                    print(f"👉 Testing found model: {name}...")
                    test_url = f"https://generativelanguage.googleapis.com/v1beta/{name}:generateContent?key={API_KEY}"
                    headers = {'Content-Type': 'application/json'}
                    payload = {"contents": [{"parts": [{"text": "Hi"}]}]}
                    
                    try:
                        r = requests.post(test_url, headers=headers, data=json.dumps(payload))
                        if r.status_code == 200:
                            print(f"✅ BINGO! Locked on: {name}")
                            WORKING_MODEL = name
                            break # Mil gaya! Loop todo
                        else:
                            print(f"⚠️ {name} failed ({r.status_code}).")
                    except:
                        continue
    else:
        print(f"❌ List fetch failed: {response.status_code}")

except Exception as e:
    print(f"❌ Connection Error: {e}")

# Fallback (Agar list fail ho jaye to zabardasti ye try karo)
if not WORKING_MODEL:
    print("⚠️ Scanning failed. Forcing 'models/gemini-1.5-flash'...")
    WORKING_MODEL = "models/gemini-1.5-flash"

# --- STEP 2: GENERATE FUNCTION ---
def generate(prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/{WORKING_MODEL}:generateContent?key={API_KEY}"
    headers = {'Content-Type': 'application/json'}
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        r = requests.post(url, headers=headers, data=json.dumps(payload))
        return r.json()
    except Exception as e:
        print(f"Request Error: {e}")
        return None

# --- STEP 3: EXECUTE ---

# A. MEMORY
current_inventory = []
if os.path.exists(INVENTORY_FILE):
    with open(INVENTORY_FILE, "r") as f:
        current_inventory = [line.strip() for line in f.readlines() if line.strip()]

# B. RESEARCH
print(f"🧠 Researching using {WORKING_MODEL}...")
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
    print(f"❌ Research failed. Response: {data}")
    sys.exit(1)

new_product_idea = data['candidates'][0]['content']['parts'][0]['text'].strip()
new_product_idea = re.sub(r'[^a-zA-Z0-9_ ]', '', new_product_idea)
print(f"💡 IDEA: {new_product_idea}")

# C. BUILD
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

