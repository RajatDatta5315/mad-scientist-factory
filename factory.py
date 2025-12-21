import requests
import json
import re
import sys
import os
import random
import urllib.parse
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

print("--- 🏭 FACTORY: STABLE DIFFUSION + JSON DB (FIXED) ---")

# 👇 SECRETS
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
PAYPAL_EMAIL = os.environ.get("PAYPAL_EMAIL")
HF_TOKEN = os.environ.get("HF_TOKEN")

if not GROQ_API_KEY:
    print("❌ ERROR: GROQ Key Missing.")
    sys.exit(1)

DB_FILE = "products.json"
WEBSITE_FILE = "index.html"

# --- 1. IMAGE GENERATOR (HUGGING FACE SDXL) ---
def generate_image(prompt):
    if not HF_TOKEN:
        print("⚠️ HF_TOKEN missing. Using fallback.")
        return "https://images.unsplash.com/photo-1642427749670-f20e2e76ed8c?auto=format&fit=crop&w=800&q=80"
    
    API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    full_prompt = f"high quality 3d render of software dashboard, {prompt}, isometric view, dark mode, neon green accents, photorealistic, 8k, unreal engine 5 render, clean ui, minimalist"
    
    payload = {"inputs": full_prompt}
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        if response.status_code == 200:
            filename = f"mockup_{int(time.time())}.jpg"
            with open(filename, "wb") as f:
                f.write(response.content)
            return filename
        else:
            print(f"⚠️ Image Gen Failed: {response.text}")
    except Exception as e:
        print(f"⚠️ Image Error: {e}")
    
    return "https://images.unsplash.com/photo-1642427749670-f20e2e76ed8c?auto=format&fit=crop&w=800&q=80"

# --- 2. TEXT GENERATOR ---
def generate_text(prompt):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "You are a coding engine. Output ONLY JSON or HTML code. Do not speak."},
            {"role": "user", "content": prompt}
        ]
    }
    try:
        r = requests.post(url, headers=headers, data=json.dumps(payload))
        if r.status_code == 200: 
            return r.json()['choices'][0]['message']['content']
    except: pass
    return None

def clean_code(text, type="html"):
    text = text.replace("```html", "").replace("```json", "").replace("```", "")
    if type == "html":
        match = re.search(r'<!DOCTYPE html>.*</html>', text, re.DOTALL | re.IGNORECASE)
        return match.group(0) if match else text
    return text.strip()

# --- 3. MAIN LOGIC ---

# A. LOAD DATABASE
db = []
if os.path.exists(DB_FILE):
    try:
        with open(DB_FILE, "r") as f: db = json.load(f)
    except: db = []

# B. FIND NEW IDEA
print("🧠 Thinking...")
existing_names = [p['name'] for p in db]
res = generate_text(f"List 1 High-Ticket B2B HTML Tool Idea that is NOT in this list: {existing_names}. Return ONLY the name.")
if not res: sys.exit(1)

# 🔥🔥🔥 THE FIX IS HERE: CLEAN THE NAME 🔥🔥🔥
raw_name = res.strip().replace('"', '')
# Remove HTML tags like <b>, <i>, and special chars
new_name = re.sub(r'<[^>]+>', '', raw_name).strip()
print(f"💡 Idea: {new_name}")

if new_name in existing_names:
    print("⚠️ Duplicate. Stopping.")
    sys.exit(0)

# C. GENERATE CONTENT
print("🛠️ Generating HTML...")
tool_raw = generate_text(f"Write single-file HTML for '{new_name}'. Dark Theme. Working functionality. No external CSS links. Output RAW HTML.")
tool_html = clean_code(tool_raw, "html")

# Create Safe Filename (No spaces, no slashes, no dots)
safe_filename = re.sub(r'[^a-zA-Z0-9_]', '', new_name.replace(' ', '_'))
file_name = f"{safe_filename}.html"

with open(file_name, "w") as f: f.write(tool_html)

print("🎨 Generating AI Mockup...")
image_path = generate_image(new_name)

price = random.choice(["49", "97", "199"])
paypal_link = f"[https://www.paypal.com/cgi-bin/webscr?cmd=_xclick&business=](https://www.paypal.com/cgi-bin/webscr?cmd=_xclick&business=){PAYPAL_EMAIL}&item_name={urllib.parse.quote(new_name)}&amount={price}&currency_code=USD"

# D. UPDATE DATABASE
new_entry = {
    "name": new_name,
    "desc": f"Automated Agency Asset. Premium {new_name} for scaling.",
    "price": price,
    "file": file_name,
    "image": image_path if "http" in image_path else "[https://images.unsplash.com/photo-1550751827-4bd374c3f58b?auto=format&fit=crop&w=800&q=80](https://images.unsplash.com/photo-1550751827-4bd374c3f58b?auto=format&fit=crop&w=800&q=80)",
    "link": paypal_link
}
db.insert(0, new_entry)

with open(DB_FILE, "w") as f: json.dump(db, f, indent=2)

# E. REBUILD WEBSITE (FRESH)
print("🌐 Rebuilding Website...")
html_start = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DryPaper HQ</title>
    <link href="[https://fonts.googleapis.com/css2?family=Outfit:wght@300;600;800&display=swap](https://fonts.googleapis.com/css2?family=Outfit:wght@300;600;800&display=swap)" rel="stylesheet">
    <style>
        body { background: #050505; color: #fff; font-family: 'Outfit', sans-serif; margin: 0; }
        .header { text-align: center; padding: 80px 20px; border-bottom: 1px solid #222; background: radial-gradient(circle at top, #1a1a1a, #000); }
        h1 { font-size: 3rem; background: linear-gradient(to right, #fff, #888); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 0; }
        .grid { max-width: 1200px; margin: 50px auto; display: grid; grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); gap: 40px; padding: 20px; }
        .card { background: #111; border: 1px solid #222; border-radius: 16px; overflow: hidden; transition: 0.3s; }
        .card:hover { transform: translateY(-5px); border-color: #00ff88; }
        .card img { width: 100%; height: 220px; object-fit: cover; }
        .info { padding: 25px; }
        .price { font-size: 1.5rem; font-weight: bold; color: #fff; }
        .btn { display: block; background: #fff; color: #000; text-align: center; padding: 12px; text-decoration: none; border-radius: 50px; font-weight: bold; margin-top: 15px; transition: 0.2s; }
        .btn:hover { background: #00ff88; }
    </style>
</head>
<body>
    <div class="header"><h1>DRYPAPER HQ</h1><p style="color:#666">Automated Assets for High-Ticket Agencies</p></div>
    <div class="grid">
"""

html_end = """
    </div>
</body>
</html>
"""

cards_html = ""
for item in db:
    cards_html += f"""
        <div class="card">
            <img src="{item['image']}" alt="{item['name']}">
            <div class="info">
                <h3 style="margin-top:0;">{item['name']}</h3>
                <p style="color:#888;">{item['desc']}</p>
                <div style="display:flex; justify-content:space-between; align-items:center; margin-top:20px;">
                    <span class="price">${item['price']}</span>
                    <a href="{item['file']}" class="btn">GET ACCESS</a>
                </div>
            </div>
        </div>
    """

final_html = html_start + cards_html + html_end
with open(WEBSITE_FILE, "w") as f: f.write(final_html)

# F. EMAIL
if GROQ_API_KEY:
    msg = MIMEMultipart()
    msg['From'] = os.environ.get("EMAIL_USER")
    msg['To'] = os.environ.get("TARGET_EMAIL")
    msg['Subject'] = f"💎 NEW DROP: {new_name}"
    
    body = f"New Product Live.\nName: {new_name}\nPrice: ${price}\nView: [https://www.drypaperhq.com](https://www.drypaperhq.com)"
    msg.attach(MIMEText(body, 'plain'))
    
    with open(file_name, "rb") as f:
        att = MIMEBase('application', 'octet-stream')
        att.set_payload(f.read())
        encoders.encode_base64(att)
        att.add_header('Content-Disposition', f"attachment; filename={file_name}")
        msg.attach(att)
        
    try:
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        s.login(os.environ.get("EMAIL_USER"), os.environ.get("EMAIL_PASS"))
        s.sendmail(os.environ.get("EMAIL_USER"), os.environ.get("TARGET_EMAIL"), msg.as_string())
        s.quit()
        print("✅ Email Sent")
    except: pass

print("✅ DONE")

