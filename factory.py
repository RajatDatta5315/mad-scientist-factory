import google.generativeai as genai
import os
import sys
import re
import time

# --- 1. SETUP ---
print("--- 🏭 STARTING FACTORY (OFFICIAL LIBRARY MODE) ---")

if "API_KEY" not in os.environ:
    print("❌ FATAL: API_KEY not found!")
    sys.exit(1)

API_KEY = os.environ["API_KEY"]
INVENTORY_FILE = "inventory.txt"

# Official Google Library Configuration
genai.configure(api_key=API_KEY)

# --- 2. MODEL SELECTION (Automatic Fallback) ---
def get_working_model():
    # Hum priority order mein models try karenge
    model_names = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro']
    
    for name in model_names:
        try:
            print(f"🔍 Testing Model: {name}...")
            model = genai.GenerativeModel(name)
            # Test generation
            response = model.generate_content("Test")
            if response.text:
                print(f"✅ LOCKED ON: {name}")
                return model
        except Exception as e:
            print(f"⚠️ {name} failed. Error: {str(e)[:50]}...")
            continue
    
    print("❌ ALL OFFICIAL MODELS FAILED.")
    sys.exit(1)

model = get_working_model()

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

try:
    response = model.generate_content(research_prompt)
    new_product_idea = response.text.strip()
    # Clean Name
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
Return ONLY raw HTML. Do not include markdown backticks.
"""

try:
    time.sleep(2) # Safety pause
    response = model.generate_content(design_prompt)
    
    html_code = response.text
    # Safai (Markdown hatana)
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

