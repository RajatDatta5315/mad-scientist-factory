import requests, json, re, sys, os, random, time, urllib.parse

print("--- 🏭 FACTORY: PREMIUM EDITION ---")

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
HF_TOKEN = os.environ.get("HF_TOKEN")
PAYPAL_EMAIL = os.environ.get("PAYPAL_EMAIL")
DB_FILE = "products.json"
WEBSITE_FILE = "index.html"

if not GROQ_API_KEY or not PAYPAL_EMAIL:
    print("❌ Secrets Missing.")
    sys.exit(1)

# --- 1. INTELLIGENT BRAIN ---
def ask_ai(system_prompt, user_prompt):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
        "temperature": 0.7
    }
    try:
        r = requests.post(url, headers=headers, data=json.dumps(payload))
        if r.status_code == 200: return r.json()['choices'][0]['message']['content'].strip()
    except Exception as e: print(f"⚠️ AI Error: {e}")
    return None

# --- 2. DYNAMIC MOCKUP GENERATOR ---
def generate_image(product_name, specific_vibe):
    filename = f"mockup_{int(time.time())}.jpg"
    print(f"🎨 Generating Premium Mockup for {product_name}...")
    
    # Specific prompt based on the tool's vibe
    prompt = f"high quality ui design of {product_name}, {specific_vibe}, dark mode, glassmorphism, glowing neon accents, 8k, behance style, dashboard view"
    encoded = urllib.parse.quote(prompt)
    
    try:
        url = f"https://image.pollinations.ai/prompt/{encoded}?width=800&height=500&nologo=true&model=flux"
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            with open(filename, "wb") as f: f.write(r.content)
            return filename
    except: pass
    return "https://placehold.co/800x500/000/0f0.png?text=Premium+Tool"

# --- 3. MARKET RESEARCH ---
db = []
if os.path.exists(DB_FILE):
    try: with open(DB_FILE, "r") as f: db = json.load(f)
    except: db = []

existing = [p['name'] for p in db]
print("🕵️ Researching High-Ticket Trends...")

# Naming Strategy
name = ask_ai("Output ONLY the name.", f"Suggest 1 B2B Micro-SaaS Tool Name (Calculator/Generator/Auditor). NOT in: {existing}. Max 3 words.")
name = re.sub(r'[^a-zA-Z0-9 ]', '', name).strip() if name else f"ROI_Tool_{int(time.time())}"
print(f"💎 Concept: {name}")

# --- 4. PREMIUM CODE ENGINEERING (UI UPGRADE) ---
print("🏗️ Coding Premium Interface...")
ui_prompt = f"""
Act as a Top-Tier Frontend Developer. Write a single-file HTML/JS tool: '{name}'.
DESIGN RULES:
1. Use a Modern Dark Theme (Black background, #00ff88 accents).
2. Use 'Glassmorphism' effects for cards (translucent backgrounds).
3. Use nice fonts (Inter or Poppins via Google Fonts).
4. Buttons must be gradient and rounded.
5. Layout must be centered and mobile-responsive.
FUNCTIONALITY:
1. Must be a working {name}.
2. No fake buttons. Real JS logic.
Output ONLY RAW HTML.
"""
tool_code = ask_ai("Output ONLY HTML.", ui_prompt)
tool_code = tool_code.replace("```html", "").replace("```", "")

safe_name = name.replace(" ", "_") + ".html"
with open(safe_name, "w") as f: f.write(tool_code)

# --- 5. PACKAGING ---
# AI decides the specific visual vibe for the mockup
vibe = ask_ai("Output 3 keywords.", f"Describe the UI look for {name} (e.g. 'financial chart', 'code editor', 'analytics graph').")
img = generate_image(name, vibe)

desc = ask_ai("Write 1 killer sales line.", f"Sell {name} to an agency.")
price = random.choice(["29", "49", "97"]) # Prices increased for premium feel

# STORE LINK (No Freebies)
file_url = f"https://www.drypaperhq.com/{safe_name}"
link = f"https://www.paypal.com/cgi-bin/webscr?cmd=_xclick&business={PAYPAL_EMAIL}&item_name={urllib.parse.quote(name)}&amount={price}&currency_code=USD&return={urllib.parse.quote(file_url)}"

# SAVE
db.insert(0, {"name": name, "desc": desc.replace('"', ''), "price": price, "file": safe_name, "image": img, "link": link})
with open(DB_FILE, "w") as f: json.dump(db, f, indent=2)

# UPDATE SHOWROOM
print("🌐 Updating Storefront...")
# (Same HTML update logic as before, just kept standard)
html = """<!DOCTYPE html><html lang='en'><head><meta charset='UTF-8'><meta name='viewport' content='width=device-width, initial-scale=1.0'><title>DryPaper HQ</title><link href='https://fonts.googleapis.com/css2?family=Outfit:wght@300;600;800&display=swap' rel='stylesheet'><style>body{background:#050505;color:#fff;font-family:'Outfit',sans-serif;margin:0}.header{text-align:center;padding:100px 20px}.header h1{font-size:3rem;margin-bottom:10px;background:linear-gradient(to right,#fff,#888);-webkit-background-clip:text;-webkit-text-fill-color:transparent}.grid{max-width:1200px;margin:50px auto;display:grid;grid-template-columns:repeat(auto-fill,minmax(350px,1fr));gap:40px;padding:20px}.card{background:#0a0a0a;border:1px solid #222;border-radius:20px;overflow:hidden;transition:0.3s;display:flex;flex-direction:column}.card:hover{border-color:#00ff88;transform:translateY(-10px)}.card img{width:100%;height:220px;object-fit:cover;border-bottom:1px solid #222}.info{padding:25px;flex-grow:1;display:flex;flex-direction:column}.title{font-size:1.4rem;font-weight:bold;margin-bottom:10px}.desc{color:#888;font-size:0.9rem;margin-bottom:20px;line-height:1.5}.footer{margin-top:auto;display:flex;justify-content:space-between;align-items:center}.price{font-size:1.5rem;font-weight:800;color:#fff}.btn{background:#fff;color:#000;padding:10px 25px;border-radius:50px;text-decoration:none;font-weight:bold;transition:0.2s}.btn:hover{background:#00ff88;box-shadow:0 0 15px rgba(0,255,136,0.3)}</style></head><body><div class='header'><h1>DRYPAPER HQ</h1><p style='color:#666'>Premium Utility Assets</p></div><div class='grid'>"""
for item in db:
    html += f"<div class='card'><img src='{item['image']}'><div class='info'><div class='title'>{item['name']}</div><div class='desc'>{item['desc']}</div><div class='footer'><div class='price'>${item['price']}</div><a href='{item['link']}' class='btn'>GET ACCESS</a></div></div></div>"
html += "</div></body></html>"
with open(WEBSITE_FILE, "w") as f: f.write(html)

print("✅ Factory Upgrade Complete.")

