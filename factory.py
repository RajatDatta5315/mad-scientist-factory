import requests
import json
import re
import sys
import time
import os
import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

print("--- 🏭 STARTING FACTORY (INFINITE AMMO MODE) ---")

# 👇👇👇 YAHAN APNI SAARI KEYS DAAL (Comma laga ke) 👇👇👇
API_KEYS = [
    "AIzaSyCqUCRX3nEzLzBKHrm0lZB_EN6h4aUFGs4",
    "AIzaSyDr2-hEXZRlRfoDGYlZ8J2J6k0zwsJXF5Y",
    "AIzaSyBttt7j1uFig01pysOf2gv9G2_URJufmvw" 
]
# 👆👆👆👆👆👆👆👆👆👆👆👆👆👆👆👆👆👆👆👆👆👆👆👆👆👆

# Remove placeholders
VALID_KEYS = [k for k in API_KEYS if "KEY_NUMBER" not in k and "YAHAN" not in k]

if not VALID_KEYS:
    print("❌ ERROR: Ek bhi valid Key nahi mili list mein!")
    sys.exit(1)

CURRENT_KEY_INDEX = 0
INVENTORY_FILE = "inventory.txt"
WEBSITE_FILE = "index.html"

# Model: Hum 2.0 Flash Exp use karenge (Safety Off) kyunki wahi connect hua tha last time
WORKING_MODEL = "models/gemini-2.0-flash-exp"

def get_current_key():
    return VALID_KEYS[CURRENT_KEY_INDEX]

def switch_key():
    global CURRENT_KEY_INDEX
    if CURRENT_KEY_INDEX < len(VALID_KEYS) - 1:
        CURRENT_KEY_INDEX += 1
        print(f"🔄 Switching to API KEY #{CURRENT_KEY_INDEX + 1}...")
        return True
    else:
        print("❌ SAB KEYS KHATAM HO GAYI! Ab koi option nahi bacha.")
        return False

def generate(prompt):
    while True:
        api_key = get_current_key()
        url = f"https://generativelanguage.googleapis.com/v1beta/{WORKING_MODEL}:generateContent?key={api_key}"
        headers = {'Content-Type': 'application/json'}
        
        # 🔥 SAFETY OFF
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "safetySettings": [
                { "category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE" },
                { "category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE" },
                { "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE" },
                { "category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE" }
            ]
        }
        
        try:
            r = requests.post(url, headers=headers, data=json.dumps(payload))
            
            if r.status_code == 200:
                return r.json()
            
            elif r.status_code == 429: # QUOTA FULL
                print(f"⚠️ Key #{CURRENT_KEY_INDEX + 1} Quota Full!")
                if switch_key():
                    continue # Retry with new key
                else:
                    return None # Sab keys mar gayi
            
            else:
                print(f"⚠️ Google Error {r.status_code}: {r.text}")
                return None
                
        except Exception as e:
            print(f"⚠️ Connection Error: {e}")
            return None

# --- 2. RESEARCH ---
current_inventory = []
if os.path.exists(INVENTORY_FILE):
    with open(INVENTORY_FILE, "r") as f:
        current_inventory = [line.strip() for line in f.readlines() if line.strip()]

print(f"🧠 Researching using Key #{CURRENT_KEY_INDEX + 1}...")
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
    print("❌ Research Failed. Sab keys try kar li.")
    # Fallback
    new_product_idea = "Agency_Sales_Script_Template"
else:
    new_product_idea = data['candidates'][0]['content']['parts'][0]['text'].strip()
    new_product_idea = re.sub(r'[^a-zA-Z0-9_ ]', '', new_product_idea)

print(f"💡 Idea: {new_product_idea}")

# --- 3. BUILD HTML ---
print(f"🛠️ Building HTML...")
design_prompt = f"""
Write HTML for "{new_product_idea}".
Theme: #121212 Dark Mode.
Feature: Large 'DOWNLOAD AS PDF' button (window.print).
Feature: Editable content.
Return ONLY raw HTML.
"""
time.sleep(1)
data = generate(design_prompt)

if not data or 'candidates' not in data:
    print("❌ Build Failed.")
    sys.exit(1)

html_code = data['candidates'][0]['content']['parts'][0]['text'].replace("```html", "").replace("```", "")
html_filename = f"{new_product_idea.replace(' ', '_')}.html"
with open(html_filename, "w") as f:
    f.write(html_code)

# --- 4. SOCIAL MEDIA CONTENT ---
print(f"📢 Generating Viral Content...")
marketing_prompt = f"""
For product: "{new_product_idea}".
1. Website Description.
2. Twitter Thread.
3. Instagram Caption.
4. Facebook Post.

Format:
WEBSITE_DESC: [text]
TWITTER: [text]
INSTAGRAM: [text]
FACEBOOK: [text]
"""
time.sleep(1)
data = generate(marketing_prompt)

marketing_text = "Check out this tool!"
web_desc = "New Agency Tool"

if data and 'candidates' in data:
    marketing_text = data['candidates'][0]['content']['parts'][0]['text']
    try:
        web_desc = marketing_text.split("WEBSITE_DESC:")[1].split("TWITTER:")[0].strip()
    except:
        pass

# --- 5. WEBSITE UPDATE ---
print("🌐 Updating Website...")
if os.path.exists(WEBSITE_FILE):
    with open(WEBSITE_FILE, "r") as f:
        html_content = f.read()
    
    today = datetime.date.today()
    new_card = f"""
    <div class="product-card">
        <div class="date">{today}</div>
        <div class="product-title">{new_product_idea}</div>
        <div class="product-desc">{web_desc}</div>
        <a href="{html_filename}" class="btn" target="_blank">OPEN TOOL</a>
    </div>
    """
    
    if "" in html_content:
        new_html = html_content.replace("", new_card)
        with open(WEBSITE_FILE, "w") as f:
            f.write(new_html)
        print("✅ Website Updated!")

# Save Inventory
with open(INVENTORY_FILE, "a") as f:
    f.write(f"\n{new_product_idea}")

# --- 6. EMAIL ---
EMAIL_USER = os.environ.get("EMAIL_USER")
EMAIL_PASS = os.environ.get("EMAIL_PASS")
TARGET_EMAIL = os.environ.get("TARGET_EMAIL")

if EMAIL_USER and EMAIL_PASS:
    msg = MIMEMultipart()
    msg['From'] = EMAIL_USER
    msg['To'] = TARGET_EMAIL
    msg['Subject'] = f"🚀 New Drop: {new_product_idea}"
    
    body = f"""
    BOSS, INFINITE AMMO DEPLOYED!
    
    🌐 Your Site: https://RajatDatta5315.github.io/mad-scientist-factory/
    
    ----- SOCIAL MEDIA COPY PASTE -----
    {marketing_text}
    """
    msg.attach(MIMEText(body, 'plain'))

    attachment = open(html_filename, "rb")
    p = MIMEBase('application', 'octet-stream')
    p.set_payload((attachment).read())
    encoders.encode_base64(p)
    p.add_header('Content-Disposition', "attachment; filename= %s" % html_filename)
    msg.attach(p)

    try:
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        s.login(EMAIL_USER, EMAIL_PASS)
        s.sendmail(EMAIL_USER, TARGET_EMAIL, msg.as_string())
        s.quit()
        print("✅ Email Sent!")
    except Exception as e:
        print(f"❌ Email Failed: {e}")

print("✅ DONE.")

