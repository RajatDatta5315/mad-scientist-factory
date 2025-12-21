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

print("--- 🏭 FACTORY START: REAL AI IMAGES & CLEAN CODE ---")

# 👇👇👇 DATA BHARO 👇👇👇
GROQ_API_KEY = "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"
PAYPAL_EMAIL = "Rajatdatta099@gmail.com"
# 👆👆👆👆👆👆👆👆👆👆👆

if "YAHAN" in GROQ_API_KEY:
    sys.exit(1)

INVENTORY_FILE = "inventory.txt"
WEBSITE_FILE = "index.html"

# --- HELPER: CLEANER ---
def clean_llm_response(text):
    # Remove Markdown
    text = text.replace("```html", "").replace("```css", "").replace("```", "")
    # Find HTML content only
    match = re.search(r'<!DOCTYPE html>.*</html>', text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(0)
    return text

def generate(prompt):
    url = "[https://api.groq.com/openai/v1/chat/completions](https://api.groq.com/openai/v1/chat/completions)"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "system", "content": "You are an expert developer. Output ONLY raw code. Do not speak."}, {"role": "user", "content": prompt}]
    }
    try:
        r = requests.post(url, headers=headers, data=json.dumps(payload))
        if r.status_code == 200: return r.json()['choices'][0]['message']['content']
    except: pass
    return None

# --- 1. RESEARCH ---
current_inventory = []
if os.path.exists(INVENTORY_FILE):
    with open(INVENTORY_FILE, "r") as f:
        current_inventory = [line.strip() for line in f.readlines() if line.strip()]

# Check Website Content
existing_site_content = ""
if os.path.exists(WEBSITE_FILE):
    with open(WEBSITE_FILE, "r") as f: existing_site_content = f.read()

res = generate(f"Current list: {current_inventory}. Suggest 1 NEW High-Ticket Agency HTML Tool. Name only.")
if not res: sys.exit(1)

new_product = res.strip().replace('"', '').replace("'", "")
clean_name = re.sub(r'[^a-zA-Z0-9_ ]', '', new_product)
file_base = clean_name.replace(' ', '_')

# STRICT DUPLICATE CHECK
if clean_name in current_inventory or clean_name in existing_site_content:
    print(f"⚠️ {clean_name} exists. Skipping.")
    sys.exit(0)

# --- 2. BUILD TOOL (CLEAN) ---
print("🛠️ Building Tool...")
tool_raw = generate(f"Write HTML for '{clean_name}'. Dark Mode. Export PDF button. Editable content. RAW HTML only. No comments.")
if tool_raw:
    tool_clean = clean_llm_response(tool_raw)
    with open(f"{file_base}_TOOL.html", "w") as f: f.write(tool_clean)

# --- 3. PRICING & REAL AI MOCKUP ---
price = random.choice(["29", "49", "97"])
paypal_url = f"[https://www.paypal.com/cgi-bin/webscr?cmd=_xclick&business=](https://www.paypal.com/cgi-bin/webscr?cmd=_xclick&business=){PAYPAL_EMAIL}&item_name={urllib.parse.quote(clean_name)}&amount={price}&currency_code=USD"

# 🔥 POLLINATIONS AI (REAL IMAGE GENERATION) 🔥
image_prompt = f"Product mockup of {clean_name}, dark background, neon green accent lighting, high tech, 3d isometric, 8k render, professional"
encoded_prompt = urllib.parse.quote(image_prompt)
mockup_url = f"[https://image.pollinations.ai/prompt/](https://image.pollinations.ai/prompt/){encoded_prompt}?width=600&height=400&nologo=true"

print(f"✍️ Sales Page (${price})...")
blog_raw = generate(f"Write Sales Page HTML for '{clean_name}'. Price ${price}. Buy Link '{paypal_url}'. Theme: Dark/Neon. Include CSS inside <style>. Output ONLY HTML.")
if blog_raw:
    blog_clean = clean_llm_response(blog_raw)
    with open(f"{file_base}_BLOG.html", "w") as f: f.write(blog_clean)

# --- 4. GENERATE DESCRIPTION ---
short_desc = generate(f"Write a 10-word description for '{clean_name}'. No quotes.")
if short_desc: short_desc = short_desc.replace('"', '')

# --- 5. UPDATE STORE ---
print("🌐 Updating Store...")
card_html = f"""
<div class="card">
    <div class="mockup">
        <img src="{mockup_url}" alt="{clean_name}" loading="lazy">
    </div>
    <div class="content">
        <div class="tag">FRESH DROP</div>
        <div class="title">{clean_name}</div>
        <div class="desc">{short_desc}</div>
        <div class="footer">
            <div class="price">${price}</div>
            <a href="{file_base}_BLOG.html" class="btn">GET ACCESS</a>
        </div>
    </div>
</div>
"""

if "" in existing_site_content:
    new_content = existing_site_content.replace("", card_html)
    with open(WEBSITE_FILE, "w") as f: f.write(new_content)

with open(INVENTORY_FILE, "a") as f: f.write(f"\n{clean_name}")

# --- 6. EMAIL ---
EMAIL_USER = os.environ.get("EMAIL_USER")
EMAIL_PASS = os.environ.get("EMAIL_PASS")
TARGET_EMAIL = os.environ.get("TARGET_EMAIL")

if EMAIL_USER and EMAIL_PASS:
    msg = MIMEMultipart()
    msg['From'] = EMAIL_USER
    msg['To'] = TARGET_EMAIL
    msg['Subject'] = f"💎 LIVE: {clean_name}"
    body = f"Mockup: {mockup_url}\nPayPal: {paypal_url}\nSite: [https://www.drypaperhq.com](https://www.drypaperhq.com)"
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

