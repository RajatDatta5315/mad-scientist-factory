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
import random

print("--- 🏭 STARTING FACTORY (PREMIUM STORE MODE) ---")

# 👇👇👇 PASTE GROQ KEY 👇👇👇
GROQ_API_KEY = "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"
# 👆👆👆👆👆👆👆👆👆👆👆👆

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
        "messages": [{"role": "system", "content": "You are a senior product developer and copywriter."}, {"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    try:
        r = requests.post(url, headers=headers, data=json.dumps(payload))
        if r.status_code == 200: return r.json()['choices'][0]['message']['content']
    except: pass
    return None

# --- 1. RESEARCH (NO DUPLICATES) ---
current_inventory = []
if os.path.exists(INVENTORY_FILE):
    with open(INVENTORY_FILE, "r") as f:
        current_inventory = [line.strip() for line in f.readlines() if line.strip()]

print("🧠 Researching unique ideas...")
res = generate(f"Current list: {current_inventory}. Suggest 1 NEW High-Ticket Agency HTML Tool. Name only. No chars.")
if not res: sys.exit(1)

new_product = res.strip().replace('"', '').replace("'", "")
clean_name = re.sub(r'[^a-zA-Z0-9_ ]', '', new_product)
file_base = clean_name.replace(' ', '_')

# DUPLICATE CHECK
if clean_name in current_inventory:
    print("⚠️ Duplicate detected. Aborting to keep store clean.")
    sys.exit(0)

print(f"💡 Green Light: {clean_name}")

# --- 2. BUILD TOOL (THE PRODUCT) ---
print("🛠️ Building Tool...")
tool_html = generate(f"Write professional HTML/CSS/JS for '{clean_name}'. Dark Mode (#111). Feature: 'Export PDF' button. Editable fields. Return RAW HTML.")
tool_html = tool_html.replace("```html", "").replace("```", "")
with open(f"{file_base}_TOOL.html", "w") as f: f.write(tool_html)

# --- 3. GENERATE BLOG / SALES PAGE ---
print("✍️ Writing Sales Blog...")
price = random.choice(["29", "39", "49", "97"])
blog_prompt = f"""
Write a SEO-Optimized Sales Page (HTML) for '{clean_name}'.
Price: ${price}.
Structure:
1. Catchy Headline.
2. Problem (Agitation).
3. Solution (The Tool).
4. Features List.
5. "Buy Now" button (Link it to '#', we add payment later).
Theme: Dark Mode (#050505), Neon accents.
Return RAW HTML.
"""
blog_html = generate(blog_prompt)
blog_html = blog_html.replace("```html", "").replace("```", "")
with open(f"{file_base}_BLOG.html", "w") as f: f.write(blog_html)

# --- 4. UPDATE STOREFRONT (PREMIUM UI) ---
print("🌐 Updating Storefront...")
if os.path.exists(WEBSITE_FILE):
    with open(WEBSITE_FILE, "r") as f: content = f.read()
    
    # Check duplicate in HTML
    if clean_name in content:
        print("⚠️ Entry exists in HTML. Skipping update.")
    else:
        # Create Premium Card HTML
        card_html = f"""
        <div class="card">
            <div class="card-img-placeholder">📄</div>
            <div class="card-body">
                <div class="tag">NEW DROP</div>
                <div class="title">{clean_name}</div>
                <div class="desc">Automated solution for modern agencies. Boost efficiency today.</div>
                <div class="price-row">
                    <div class="price">${price}</div>
                    <a href="{file_base}_BLOG.html" class="btn">VIEW DETAILS</a>
                </div>
            </div>
        </div>
        """
        
        if "" in content:
            new_content = content.replace("", card_html)
            with open(WEBSITE_FILE, "w") as f: f.write(new_content)
            print("✅ Store Updated!")

# Update Inventory
with open(INVENTORY_FILE, "a") as f: f.write(f"\n{clean_name}")

# --- 5. EMAIL NOTIFICATION ---
EMAIL_USER = os.environ.get("EMAIL_USER")
EMAIL_PASS = os.environ.get("EMAIL_PASS")
TARGET_EMAIL = os.environ.get("TARGET_EMAIL")

if EMAIL_USER and EMAIL_PASS:
    msg = MIMEMultipart()
    msg['From'] = EMAIL_USER
    msg['To'] = TARGET_EMAIL
    msg['Subject'] = f"💎 PREMIUM DROP: {clean_name}"
    body = f"New Product Live on Store!\nPrice Set: ${price}\nCheck Site: https://drypaperhq.com (or github link)"
    msg.attach(MIMEText(body, 'plain'))
    
    # Attach Tool
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
        print("✅ Email Sent!")
    except: print("❌ Email Fail")

print("✅ DONE.")

