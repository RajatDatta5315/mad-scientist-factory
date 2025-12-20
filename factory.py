import requests
import json
import re
import sys
import time
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

print("--- 🏭 STARTING FACTORY (EMAIL DELIVERY MODE) ---")

# --- CONFIG ---
API_KEY = "AIzaSyAf9U_Rz-Ran-krt6pygrrVNuOpsG72iug" # ⚠️ WARNING: Apni Key wapis yahan paste kar!
EMAIL_USER = os.environ.get("EMAIL_USER")
EMAIL_PASS = os.environ.get("EMAIL_PASS")
TARGET_EMAIL = os.environ.get("TARGET_EMAIL")

if "YAHAN" in API_KEY:
    print("❌ ERROR: API Key missing in code!")
    sys.exit(1)

INVENTORY_FILE = "inventory.txt"

# --- 1. CONNECT TO BRAIN ---
list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"
WORKING_MODEL = "models/gemini-1.5-flash"
try:
    response = requests.get(list_url)
    if response.status_code == 200:
        data = response.json()
        for m in data.get('models', []):
            if 'generateContent' in m.get('supportedGenerationMethods', []):
                WORKING_MODEL = m['name']
                break
except:
    pass
print(f"✅ Connected: {WORKING_MODEL}")

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
new_product_idea = data['candidates'][0]['content']['parts'][0]['text'].strip()
new_product_idea = re.sub(r'[^a-zA-Z0-9_ ]', '', new_product_idea)
print(f"💡 Idea: {new_product_idea}")

# --- 3. BUILD HTML (WITH DOWNLOAD BUTTON) ---
print(f"🛠️ Building HTML...")
design_prompt = f"""
Write HTML for "{new_product_idea}".
Theme: #121212 Dark Mode.
CRITICAL FEATURE: Include a large, styled button at the top right that says 'DOWNLOAD AS PDF'.
The button must use 'window.print()' onclick event.
Feature: Editable content (<span contenteditable>).
Return ONLY raw HTML.
"""
time.sleep(1)
data = generate(design_prompt)
html_code = data['candidates'][0]['content']['parts'][0]['text'].replace("```html", "").replace("```", "")
html_filename = f"{new_product_idea.replace(' ', '_')}.html"
with open(html_filename, "w") as f:
    f.write(html_code)

# --- 4. MARKETING ---
print(f"💰 Creating Marketing Assets...")
marketing_prompt = f"""
Create Payhip Marketing for: "{new_product_idea}".
1. Title
2. Description (Pain/Solution)
3. 10 Tags
4. 3 Image Prompts
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

# --- 5. EMAIL DELIVERY SYSTEM ---
print("📧 Sending Email to Boss...")

if not EMAIL_USER or not EMAIL_PASS:
    print("⚠️ Email Secrets missing. Skipping email.")
else:
    msg = MIMEMultipart()
    msg['From'] = EMAIL_USER
    msg['To'] = TARGET_EMAIL
    msg['Subject'] = f"New Product Ready: {new_product_idea}"
    
    body = "Here are your daily generated files via Mad Scientist Factory."
    msg.attach(MIMEText(body, 'plain'))

    # Attach HTML
    attachment = open(html_filename, "rb")
    p = MIMEBase('application', 'octet-stream')
    p.set_payload((attachment).read())
    encoders.encode_base64(p)
    p.add_header('Content-Disposition', "attachment; filename= %s" % html_filename)
    msg.attach(p)

    # Attach Marketing Text
    attachment2 = open(marketing_filename, "rb")
    p2 = MIMEBase('application', 'octet-stream')
    p2.set_payload((attachment2).read())
    encoders.encode_base64(p2)
    p2.add_header('Content-Disposition', "attachment; filename= %s" % marketing_filename)
    msg.attach(p2)

    try:
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        s.login(EMAIL_USER, EMAIL_PASS)
        text = msg.as_string()
        s.sendmail(EMAIL_USER, TARGET_EMAIL, text)
        s.quit()
        print("✅ EMAIL SENT SUCCESSFULLY!")
    except Exception as e:
        print(f"❌ Email Failed: {e}")

print("✅ DONE.")

