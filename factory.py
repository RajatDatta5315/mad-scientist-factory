import requests
import json
import re
import sys
import os
import random
import urllib.parse
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

print("--- 🏭 FACTORY START: PREMIUM & CLEAN MODE ---")

# 👇👇👇 CONFIGURATION 👇👇👇
GROQ_API_KEY = "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"
PAYPAL_EMAIL = "Rajatdatta099@gmail.com " # <-- PayPal Email
# 👆👆👆👆👆👆👆👆👆👆👆👆👆

if "YAHAN" in GROQ_API_KEY:
    print("❌ ERROR: Key missing!")
    sys.exit(1)

INVENTORY_FILE = "inventory.txt"
WEBSITE_FILE = "index.html"

# --- HELPER: GROQ CONNECT ---
def generate(prompt):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "system", "content": "You are an elite UX copywriter and developer."}, {"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    try:
        r = requests.post(url, headers=headers, data=json.dumps(payload))
        if r.status_code == 200: return r.json()['choices'][0]['message']['content']
    except: pass
    return None

# --- 1. SMART RESEARCH (NO DUPLICATES) ---
current_inventory = []
if os.path.exists(INVENTORY_FILE):
    with open(INVENTORY_FILE, "r") as f:
        current_inventory = [line.strip() for line in f.readlines() if line.strip()]

# Check Website Content to avoid visual duplicates
existing_site_content = ""
if os.path.exists(WEBSITE_FILE):
    with open(WEBSITE_FILE, "r") as f: existing_site_content = f.read()

print("🧠 Researching unique high-ticket idea...")
res = generate(f"Current list: {current_inventory}. Suggest 1 NEW High-Ticket Agency HTML Tool/Contract. Name only. No special chars.")
if not res: sys.exit(1)

new_product = res.strip().replace('"', '').replace("'", "")
clean_name = re.sub(r'[^a-zA-Z0-9_ ]', '', new_product)
file_base = clean_name.replace(' ', '_')

# STRICT DUPLICATE CHECK
if clean_name in current_inventory or clean_name in existing_site_content:
    print(f"⚠️ '{clean_name}' already exists. Skipping to keep store clean.")
    sys.exit(0)

print(f"💡 Green Light: {clean_name}")

# --- 2. BUILD TOOL (PREMIUM) ---
print("🛠️ Building Tool...")
tool_html = generate(f"Write professional HTML/CSS/JS for '{clean_name}'. Theme: Dark/Neon. Feature: 'Export PDF' button. Editable contenteditable areas. Return RAW HTML only.")
if tool_html:
    tool_html = tool_html.replace("```html", "").replace("```", "")
    with open(f"{file_base}_TOOL.html", "w") as f: f.write(tool_html)

# --- 3. PRICING & SALES PAGE ---
price = random.choice(["29", "49", "97"])
paypal_url = f"https://www.paypal.com/cgi-bin/webscr?cmd=_xclick&business={PAYPAL_EMAIL}&item_name={urllib.parse.quote(clean_name)}&amount={price}&currency_code=USD"

print(f"✍️ Writing Sales Page (${price})...")
blog_prompt = f"""
Write a Premium Sales Page (HTML) for '{clean_name}'.
Price: ${price}.
Buy Link: "{paypal_url}"
Style: Dark mode, Apple-style typography.
Include: Headline, Pain Points, Solution, Features, FAQ.
Return RAW HTML.
"""
blog_html = generate(blog_prompt)
if blog_html:
    blog_html = blog_html.replace("```html", "").replace("```", "")
    with open(f"{file_base}_BLOG.html", "w") as f: f.write(blog_html)

# --- 4. GENERATE CARD DESCRIPTION ---
short_desc = generate(f"Write a 1-sentence punchy description for '{clean_name}' (max 10 words).")
short_desc = short_desc.replace('"', '')

# --- 5. UPDATE STOREFRONT (PREMIUM CARD) ---
print("🌐 Updating Storefront...")
card_html = f"""
<div class="card">
    <div class="mockup" style="background: linear-gradient({random.randint(0,360)}deg, #111 0%, #222 100%);">
        </div>
    <div class="content">
        <div class="tag">NEW ARRIVAL</div>
        <div class="title">{clean_name}</div>
        <div class="desc">{short_desc}</div>
        <div class="footer-row">
            <div class="price">${price}</div>
            <a href="{file_base}_BLOG.html" class="btn">View Details</a>
        </div>
    </div>
</div>
"""

if "" in existing_site_content:
    new_content = existing_site_content.replace("", card_html)
    with open(WEBSITE_FILE, "w") as f: f.write(new_content)
    print("✅ Store Updated!")

# Update Inventory
with open(INVENTORY_FILE, "a") as f: f.write(f"\n{clean_name}")

# --- 6. EMAIL ---
EMAIL_USER = os.environ.get("EMAIL_USER")
EMAIL_PASS = os.environ.get("EMAIL_PASS")
TARGET_EMAIL = os.environ.get("TARGET_EMAIL")

if EMAIL_USER and EMAIL_PASS:
    msg = MIMEMultipart()
    msg['From'] = EMAIL_USER
    msg['To'] = TARGET_EMAIL
    msg['Subject'] = f"💎 LIVE: {clean_name} (${price})"
    body = f"Product is LIVE.\nPrice: ${price}\nPayPal: {paypal_url}\nSite: https://www.drypaperhq.com"
    msg.attach(MIMEText(body, 'plain'))
    if os.path.exists(f"{file_base}_TOOL.html"):
        att = MIMEBase('application', 'octet-stream')
        with open(f"{file_base}_TOOL.html", "rb") as f: att.set_payload(f.read())
        encoders.encode_base64(att)
        att.add_header('Content-Disposition', f"attachment; filename={file_base}_TOOL.html")
        msg.attach(att)
    try:
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        s.login(EMAIL_USER, EMAIL_PASS)
        s.sendmail(EMAIL_USER, TARGET_EMAIL, msg.as_string())
        s.quit()
    except: pass

print("✅ DONE.")

