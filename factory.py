import requests, json, re, sys, os, random, time, urllib.parse

print("--- 🏭 FACTORY: FINAL POLISH ---")

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
HF_TOKEN = os.environ.get("HF_TOKEN")
PAYPAL_EMAIL = os.environ.get("PAYPAL_EMAIL")
DB_FILE = "products.json"
WEBSITE_FILE = "index.html"

if not GROQ_API_KEY or not PAYPAL_EMAIL:
    print("❌ Critical: Secrets Missing.")
    sys.exit(1)

# --- 1. DUAL-ENGINE IMAGE GENERATOR (No Watermark) ---
def generate_image(product_name, specific_prompt):
    filename = f"mockup_{int(time.time())}.jpg"
    
    # OPTION A: HUGGING FACE (SDXL)
    if HF_TOKEN:
        print("🎨 Trying Hugging Face SDXL...")
        API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
        headers = {"Authorization": f"Bearer {HF_TOKEN}"}
        full_prompt = f"isometric view of a futuristic software dashboard for {product_name}, {specific_prompt}, dark mode UI, neon green data charts, highly detailed, 8k resolution, unreal engine 5 render, professional tech design, no text"
        
        payload = {"inputs": full_prompt}
        try:
            r = requests.post(API_URL, headers=headers, json=payload)
            if r.status_code == 200:
                with open(filename, "wb") as f: f.write(r.content)
                print("✅ Image Generated via Hugging Face")
                return filename
        except: print("⚠️ Hugging Face Failed. Switching to Backup.")

    # OPTION B: POLLINATIONS (Flux Model - No Watermark Hack)
    print("🎨 Trying Backup (Pollinations No-Logo)...")
    try:
        # 'nologo=true' removes watermark, 'model=flux' gives high quality
        prompt_encoded = urllib.parse.quote(f"futuristic dark software interface {product_name} {specific_prompt} neon glow data vizualisation 8k")
        url = f"https://image.pollinations.ai/prompt/{prompt_encoded}?width=800&height=450&nologo=true&model=flux"
        
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            with open(filename, "wb") as f: f.write(r.content)
            print("✅ Image Generated via Backup")
            return filename
    except Exception as e:
        print(f"❌ Backup Failed: {e}")

    # LAST RESORT (Clean Text Placeholder)
    safe_text = urllib.parse.quote(product_name)
    return f"https://placehold.co/800x450/050505/00ff88.png?text={safe_text}&font=montserrat"

# --- 2. TEXT BRAIN ---
def generate_text(prompt):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": "llama-3.3-70b-versatile", "messages": [{"role": "system", "content": "Output ONLY raw text/code."}, {"role": "user", "content": prompt}]}
    try:
        r = requests.post(url, headers=headers, data=json.dumps(payload))
        if r.status_code == 200: return r.json()['choices'][0]['message']['content']
    except: pass
    return "Premium Agency Asset"

# --- 3. LOAD DB (FIXED SYNTAX HERE) ---
db = []
if os.path.exists(DB_FILE):
    try:
        with open(DB_FILE, "r") as f:
            db = json.load(f)
    except:
        db = []

# --- 4. CREATE PRODUCT ---
existing = [p['name'] for p in db]
res = generate_text(f"Generate 1 High-Ticket AI/Agency HTML Tool Name NOT in: {existing}. Name Only.")
if not res: sys.exit(1)
new_name = re.sub(r'<[^>]+>', '', res.strip().replace('"', '')).strip()

if new_name in existing: sys.exit(0)

print(f"🛠️ Building: {new_name}")

# HTML Tool
tool_raw = generate_text(f"Write a Premium HTML Tool for '{new_name}'. Dark Theme. Single file. Output RAW HTML.")
tool_html = tool_raw.replace("```html", "").replace("```", "")
if "<!DOCTYPE" in tool_html: tool_html = tool_html[tool_html.find("<!DOCTYPE"):]
if "</html>" in tool_html: tool_html = tool_html[:tool_html.find("</html>")+7]

safe_name = re.sub(r'[^a-zA-Z0-9_]', '', new_name.replace(' ', '_')) + ".html"
with open(safe_name, "w") as f: f.write(tool_html)

# Image & Metadata
visual_desc = generate_text(f"Describe the UI of '{new_name}' in 5 keywords for image generation (e.g. charts, analytics, dark mode).")
img = generate_image(new_name, visual_desc) 
desc = generate_text(f"Write 2 sentence catchy sales copy for '{new_name}'.")

# PayPal Link
price = random.choice(["49", "97", "149"])
link = f"https://www.paypal.com/cgi-bin/webscr?cmd=_xclick&business={PAYPAL_EMAIL}&item_name={urllib.parse.quote(new_name)}&amount={price}&currency_code=USD"

# --- 5. SAVE TO DB ---
db.insert(0, {
    "name": new_name, 
    "desc": desc.replace('"', ''), 
    "price": price, 
    "file": safe_name, 
    "image": img, 
    "link": link 
})

with open(DB_FILE, "w") as f: json.dump(db, f, indent=2)

# --- 6. UPDATE WEBSITE ---
print("🌐 Updating Website...")
html = """<!DOCTYPE html><html lang='en'><head><meta charset='UTF-8'><meta name='viewport' content='width=device-width, initial-scale=1.0'><title>DryPaper HQ</title><link href='https://fonts.googleapis.com/css2?family=Outfit:wght@300;600;800&display=swap' rel='stylesheet'><style>body{background:#050505;color:#fff;font-family:'Outfit',sans-serif;margin:0}.header{text-align:center;padding:100px 20px;background:radial-gradient(circle at top,#1a1a1a,#000)}.header h1{font-size:3.5rem;margin:0;letter-spacing:-2px;background:linear-gradient(to right,#fff,#888);-webkit-background-clip:text;-webkit-text-fill-color:transparent}.grid{max-width:1200px;margin:60px auto;display:grid;grid-template-columns:repeat(auto-fill,minmax(350px,1fr));gap:40px;padding:20px}.card{background:#0a0a0a;border:1px solid #222;border-radius:20px;overflow:hidden;transition:0.3s;display:flex;flex-direction:column;position:relative}.card:hover{border-color:#00ff88;transform:translateY(-10px);box-shadow:0 20px 40px rgba(0,0,0,0.8)}.card img{width:100%;height:240px;object-fit:cover;border-bottom:1px solid #222}.info{padding:30px;flex-grow:1;display:flex;flex-direction:column}.tag{color:#00ff88;font-size:0.8rem;text-transform:uppercase;letter-spacing:1px;margin-bottom:10px;font-weight:bold}.title{font-size:1.5rem;font-weight:800;margin-bottom:10px;line-height:1.2}.desc{color:#888;font-size:0.95rem;margin-bottom:25px;line-height:1.6}.footer{margin-top:auto;display:flex;justify-content:space-between;align-items:center;border-top:1px solid #222;padding-top:20px}.price{font-size:1.6rem;font-weight:800;color:#fff}.btn{background:#fff;color:#000;padding:12px 30px;border-radius:50px;text-decoration:none;font-weight:bold;transition:0.2s;font-size:0.9rem}.btn:hover{background:#00ff88;box-shadow:0 0 20px rgba(0,255,136,0.4)}</style></head><body><div class='header'><h1>DRYPAPER HQ</h1><p style='color:#666;font-size:1.2rem;margin-top:10px'>Premium Assets for High-Growth Agencies</p></div><div class='grid'>"""

for item in db:
    # Use image file if local, else use URL
    img_src = item['image']
    
    html += f"""
    <div class='card'>
        <img src='{img_src}' alt='{item['name']}'>
        <div class='info'>
            <div class='tag'>Premium Tool</div>
            <div class='title'>{item['name']}</div>
            <div class='desc'>{item['desc']}</div>
            <div class='footer'>
                <div class='price'>${item['price']}</div>
                <a href='{item['link']}' class='btn'>GET ACCESS</a>
            </div>
        </div>
    </div>
    """

html += "</div></body></html>"
with open(WEBSITE_FILE, "w") as f: f.write(html)

print("✅ Website Updated.")

