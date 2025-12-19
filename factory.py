import requests
import json
import os
import re  # Naya Guard: Regex for cleaning names

# --- SETUP ---
API_KEY = os.environ["API_KEY"] # Ye ab GitHub ke Secret vault se key uthayega
INVENTORY_FILE = "inventory.txt"

print("\n--- 🏭 DIGITAL PRODUCT FACTORY (SAFE MODE) ---")

# --- MODULE 0: CONNECT ---
print("🔍 Connecting to Brain...")
list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"
my_model = "models/gemini-1.5-flash"

try:
    response = requests.get(list_url)
    models_data = response.json()
    if 'models' in models_data:
        for m in models_data['models']:
            if 'generateContent' in m['supportedGenerationMethods'] and 'gemini' in m['name']:
                my_model = m['name']
                if 'flash' in m['name'] or 'pro' in m['name']:
                    break
    print(f"✅ Connected via: {my_model}")
except:
    print(f"⚠️ Using default: {my_model}")

# --- MODULE 1: MEMORY ---
print(f"📖 Reading Diary...")
current_inventory = []
if os.path.exists(INVENTORY_FILE):
    with open(INVENTORY_FILE, "r") as f:
        current_inventory = [line.strip() for line in f.readlines() if line.strip()]

print(f"✅ Avoiding {len(current_inventory)} existing products.")

# --- MODULE 2: VISIBLE DEEP RESEARCH ---
print("🧠 Researching Market Gaps (Thinking Process)...")

# Hum AI ko bolenge ki format mein jawab de taaki hum 'Reasoning' padh sakein
research_prompt = f"""
Act as a Senior Product Researcher.
Current Inventory: {current_inventory}.

Task: Find 1 High-Ticket B2B Document missing from the list.
Target: US Agencies / SaaS.

RESPONSE FORMAT:
REASONING: [Explain WHY this product is profitable in 1 sentence]
PRODUCT_NAME: [The Name]

Restrictions:
- Name must be premium but simple (No special characters like : or &).
- No Invoices/Receipts.
"""

url = f"https://generativelanguage.googleapis.com/v1beta/{my_model}:generateContent?key={API_KEY}"
headers = {'Content-Type': 'application/json'}
payload = {"contents": [{"parts": [{"text": research_prompt}]}]}

try:
    r = requests.post(url, headers=headers, data=json.dumps(payload))
    full_text = r.json()['candidates'][0]['content']['parts'][0]['text'].strip()
    
    # Text ko todna (Parsing)
    reasoning = "Research logic hidden."
    new_product_idea = "New_Product"
    
    for line in full_text.split('\n'):
        if "REASONING:" in line:
            reasoning = line.replace("REASONING:", "").strip()
        if "PRODUCT_NAME:" in line:
            new_product_idea = line.replace("PRODUCT_NAME:", "").strip()
    
    # SHOW THE RESEARCH
    print(f"\n🤔 AI LOGIC: {reasoning}")
    print(f"💡 SELECTED PRODUCT: {new_product_idea}")
    
except Exception as e:
    print(f"❌ Research Failed: {e}")
    exit()

# --- MODULE 3: THE BUILDER (Clean Filename Logic) ---
print(f"🛠️ Engineering HTML for {new_product_idea}...")

design_prompt = f"""
Write a single HTML file for "{new_product_idea}".

THEME: Cyberpunk Professional (#121212 Bg, #00FF94 Accents).
Font: 'Inter', sans-serif.

FEATURES:
1. **EDITABLE:** Use <span contenteditable="true" style="border-bottom: 1px dashed #00FF94"> for all user data.
2. **PDF BUTTON:** Add a <button onclick="window.print()">SAVE AS PDF</button>.
3. **STYLE:** Button must be big, green, bold text, centered at bottom.
4. **PRINT CSS:** @media print {{ button {{ display: none; }} body {{ background: white; color: black; }} }} 
   (Note: Print mode should be white paper friendly, screen mode is dark).

Return ONLY raw HTML.
"""

payload = {"contents": [{"parts": [{"text": design_prompt}]}]}
r = requests.post(url, headers=headers, data=json.dumps(payload))

try:
    html_code = r.json()['candidates'][0]['content']['parts'][0]['text']
    html_code = html_code.replace("```html", "").replace("```", "")

    # --- FILENAME CLEANER (Tera Issue Fix) ---
    # Ye Regex sirf A-Z, 0-9 aur underscore rakhega. Baaki sab uda dega.
    clean_name = re.sub(r'[^a-zA-Z0-9_]', '', new_product_idea.replace(' ', '_'))
    filename = f"{clean_name}.html"
    
    with open(filename, "w") as f:
        f.write(html_code)

    with open(INVENTORY_FILE, "a") as f:
        f.write(f"\n{new_product_idea}")

    print(f"\n✅ SUCCESS: {filename}")
    print("🚀 Opening file...")
    os.system(f"termux-open {filename}")

except Exception as e:
    print(f"❌ Error Saving: {e}")
