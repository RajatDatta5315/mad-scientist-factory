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

print("--- 🏭 STARTING FACTORY (GROQ POWERED ⚡) ---")

# 👇👇👇 PASTE YOUR GROQ KEY HERE (gsk_...) 👇👇👇
GROQ_API_KEY = "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"
# 👆👆👆👆👆👆👆👆👆👆👆👆👆👆👆👆👆👆👆👆

if "YAHAN" in GROQ_API_KEY:
    print("❌ ERROR: Groq Key paste kar bhai!")
    sys.exit(1)

INVENTORY_FILE = "inventory.txt"
WEBSITE_FILE = "index.html"

# --- 1. CONNECT TO GROQ ---
def generate(prompt):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Hum Llama 3 70B use karenge (Coding Beast)
    payload = {
        "model": "llama3-70b-8192",
        "messages": [
            {"role": "system", "content": "You are an expert developer and copywriter. Return ONLY the requested content. No yapping."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }
    
    try:
        r = requests.post(url, headers=headers, data=json.dumps(payload))
        if r.status_code == 200:
            return r.json()['choices'][0]['message']['content']
        else:
            print(f"⚠️ Groq Error {r.status_code}: {r.text}")
            return None
    except Exception as e:
        print(f"⚠️ Connection Error: {e}")
        return None

# --- 2. RESEARCH ---
current_inventory = []
if os.path.exists(INVENTORY_FILE):
    with open(INVENTORY_FILE, "r") as f:
        current_inventory = [line.strip() for line in f.readlines() if line.strip()]

print("🧠 Researching with Llama 3...")
research_prompt = f"""
Current Inventory: {current_inventory}.
Find 1 High-Ticket B2B HTML Document missing from list.
Target: US Agencies.
Name format: Clean, Simple, Professional. No special chars.
Return ONLY the Name. Do not write 'Here is the name'. Just the name.
"""
data = generate(research_prompt)

if not data:
    print("❌ Research Failed. Using Backup.")
    new_product_idea = "Agency_Retainer_Agreement_Template"
else:
    new_product_idea = data.strip().replace('"', '').replace("'", "")
    new_product_idea = re.sub(r'[^a-zA-Z0-9_ ]', '', new_product_idea)

print(f"💡 Idea: {new_product_idea}")

# --- 3. BUILD HTML ---
print(f"🛠️ Building HTML...")
design_prompt = f"""
Write comprehensive HTML/CSS for "{new_product_idea}".
Theme: #121212 Dark Mode.
Feature: Large 'DOWNLOAD AS PDF' button (top right) that triggers window.print().
Feature: Editable content areas (<span contenteditable>).
Style: Professional, clean, modern agency look.
Return ONLY raw HTML code. Do not start with "Here is the HTML".
"""
time.sleep(1) # Groq is fast, but let's be safe
html_code = generate(design_prompt)

if not html_code:
    print("❌ Build Failed.")
    sys.exit(1)

# Clean Markdown if Llama adds it
html_code = html_code.replace("```html", "").replace("```", "")

html_filename = f"{new_product_idea.replace(' ', '_')}.html"
with open(html_filename, "w") as f:
    f.write(html_code)

# --- 4. SOCIAL MEDIA CONTENT ---
print(f"📢 Generating Viral Content...")
marketing_prompt = f"""
For product: "{new_product_idea}".
1. Website Description (1 sentence).
2. Twitter Thread (3 tweets, Hook -> Value -> Link).
3. Instagram Caption (with 15 hashtags).
4. Facebook Post.

Format your response exactly like this:
WEBSITE_DESC: [text]
TWITTER: [text]
INSTAGRAM: [text]
FACEBOOK: [text]
"""
time.sleep(1)
marketing_text = generate(marketing_prompt)

web_desc = "A premium tool for agencies."
if marketing_text:
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
    else:
        print("⚠️ 'AUTOMATION WILL PASTE NEW PRODUCTS HERE' placeholder not found in index.html")

# Save Inventory
with open(INVENTORY_FILE, "a") as f:
    f.write(f"\n{new_product_idea}")

# --- 6. EMAIL ---
EMAIL_USER = os.environ.get("EMAIL_USER")
EMAIL_PASS = os.environ.get("EMAIL_PASS")
TARGET_EMAIL = os.environ.get("TARGET_EMAIL")

if EMAIL_USER and EMAIL_PASS:
    print("📧 Sending Email...")
    msg = MIMEMultipart()
    msg['From'] = EMAIL_USER
    msg['To'] = TARGET_EMAIL
    msg['Subject'] = f"⚡ GROQ DROP: {new_product_idea}"
    
    body = f"""
    BOSS, NEW PRODUCT VIA GROQ (Llama 3)!
    
    🌐 Site: https://RajatDatta5315.github.io/mad-scientist-factory/
    
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

