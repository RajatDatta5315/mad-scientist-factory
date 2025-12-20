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

print("--- 🏭 STARTING FACTORY (DIRECT TARGET MODE) ---")

# 👇👇👇 PASTE KEY HERE 👇👇👇
API_KEY = "AIzaSyBttt7j1uFig01pysOf2gv9G2_URJufmvw" 
# 👆👆👆👆👆👆👆👆👆👆👆👆👆👆

if "YAHAN" in API_KEY:
    print("❌ ERROR: Key paste kar bhai!")
    sys.exit(1)

INVENTORY_FILE = "inventory.txt"
WEBSITE_FILE = "index.html"

# --- 1. CONNECT (TARGET SPECIFIC MODELS) ---
# Hum robotics ya preview models ko touch bhi nahi karenge.
# Sirf ye 5 try karenge jo TEXT likhte hain.
TARGET_MODELS = [
    "models/gemini-1.5-flash",
    "models/gemini-1.5-flash-latest",
    "models/gemini-1.5-flash-001",
    "models/gemini-1.5-pro",
    "models/gemini-pro"
]

WORKING_MODEL = None
print("🔍 Testing Text Models...")

for model in TARGET_MODELS:
    url = f"https://generativelanguage.googleapis.com/v1beta/{model}:generateContent?key={API_KEY}"
    headers = {'Content-Type': 'application/json'}
    payload = {"contents": [{"parts": [{"text": "Hi"}]}]}
    
    try:
        print(f"👉 Testing {model}...")
        r = requests.post(url, headers=headers, data=json.dumps(payload))
        if r.status_code == 200:
            print(f"✅ LOCKED ON: {model}")
            WORKING_MODEL = model
            break
        else:
            print(f"⚠️ Failed: {r.status_code}")
    except:
        print("⚠️ Connection Error")
        continue

if not WORKING_MODEL:
    print("❌ ALL TARGETS FAILED. API Key check kar ya Quota khatam ho gaya hai.")
    sys.exit(1)

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
    print("❌ Research Failed. Using Backup.")
    new_product_idea = "Agency_Social_Media_Policy_Template"
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
marketing_text = data['candidates'][0]['content']['parts'][0]['text']

try:
    web_desc = marketing_text.split("WEBSITE_DESC:")[1].split("TWITTER:")[0].strip()
except:
    web_desc = "A premium tool for agencies."

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
    BOSS, WEBSITE UPDATED!
    
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

