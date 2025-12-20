import requests
import json
import re
import sys
import time
import os

print("--- 🏭 STARTING FACTORY (PRODUCT + MARKETING MODE) ---")

# 👇👇👇 PASTE KEY HERE 👇👇👇
API_KEY = "AIzaSyBttt7j1uFig01pysOf2gv9G2_URJufmvw" 
# 👆👆👆👆👆👆👆👆👆👆👆👆👆👆

if "YAHAN" in API_KEY:
    print("❌ ERROR: Bhai Key paste karna bhul gaya!")
    sys.exit(1)

INVENTORY_FILE = "inventory.txt"

# --- 1. CONNECT & FIND MODEL ---
print("🔍 Scanning for Brain...")
# (Wahi purana connection logic - Universal Search)
list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"
WORKING_MODEL = "models/gemini-1.5-flash" # Default fallback

try:
    response = requests.get(list_url)
    if response.status_code == 200:
        data = response.json()
        if 'models' in data:
            for m in data['models']:
                if 'generateContent' in m.get('supportedGenerationMethods', []):
                    WORKING_MODEL = m['name']
                    break
except:
    pass
print(f"✅ Connected to: {WORKING_MODEL}")

def generate(prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/{WORKING_MODEL}:generateContent?key={API_KEY}"
    headers = {'Content-Type': 'application/json'}
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        r = requests.post(url, headers=headers, data=json.dumps(payload))
        return r.json()
    except:
        return None

# --- 2. RESEARCH ---
current_inventory = []
if os.path.exists(INVENTORY_FILE):
    with open(INVENTORY_FILE, "r") as f:
        current_inventory = [line.strip() for line in f.readlines() if line.strip()]

print("🧠 Researching Product Idea...")
research_prompt = f"""
Act as a Product Researcher.
Current Inventory: {current_inventory}.
Find 1 High-Ticket B2B HTML Document missing from list.
Target: US Agencies.
Name format: Clean, Simple, Professional. No special chars.
Return ONLY the Name.
"""
data = generate(research_prompt)
new_product_idea = data['candidates'][0]['content']['parts'][0]['text'].strip()
new_product_idea = re.sub(r'[^a-zA-Z0-9_ ]', '', new_product_idea)
print(f"💡 IDEA: {new_product_idea}")

# --- 3. BUILD HTML ---
print(f"🛠️ Building HTML...")
design_prompt = f"""
Write HTML for "{new_product_idea}".
Theme: #121212 Dark Mode.
Feature: Editable content, Print to PDF button.
Return ONLY raw HTML.
"""
time.sleep(1)
data = generate(design_prompt)
html_code = data['candidates'][0]['content']['parts'][0]['text'].replace("```html", "").replace("```", "")
html_filename = f"{new_product_idea.replace(' ', '_')}.html"
with open(html_filename, "w") as f:
    f.write(html_code)

# --- 4. GENERATE MARKETING ASSETS (Payhip Data) ---
print(f"💰 Generating Marketing Assets...")
marketing_prompt = f"""
Act as a Copywriter & AI Art Director.
Product: "{new_product_idea}" (A dark-mode HTML template for agencies).

Create the following for Payhip:
1. SEO Optimized Title
2. Persuasive Description (Pain point -> Agitation -> Solution)
3. 10 High-Volume Tags (Comma separated)
4. 3 AI Image Prompts to generate realistic mockups (Laptop on desk style).

Format the output clearly.
"""
time.sleep(1)
data = generate(marketing_prompt)
marketing_text = data['candidates'][0]['content']['parts'][0]['text']

marketing_filename = f"{new_product_idea.replace(' ', '_')}_MARKETING.txt"
with open(marketing_filename, "w") as f:
    f.write(marketing_text)

# Save Inventory
with open(INVENTORY_FILE, "a") as f:
    f.write(f"\n{new_product_idea}")

print(f"\n✅ SUCCESS!")
print(f"📁 Product: {html_filename}")
print(f"📁 Marketing: {marketing_filename}")


