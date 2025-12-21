import requests, json, re, sys, os, random, time, urllib.parse

print("--- 🏭 FACTORY & MANAGER: PRODUCTION LINE ---")

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
HF_TOKEN = os.environ.get("HF_TOKEN")
DB_FILE = "products.json"
WEBSITE_FILE = "index.html"

if not GROQ_API_KEY:
    print("❌ Critical: GROQ Key Missing.")
    sys.exit(1)

# --- 1. IMAGE GENERATOR (Hugging Face) ---
def generate_image(prompt):
    if not HF_TOKEN: return "https://placehold.co/800x450/111/00ff88.png?text=NO+IMG+TOKEN"
    API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    payload = {"inputs": f"futuristic software dashboard, {prompt}, dark mode, neon green, 8k render, isometric, clean ui"}
    try:
        r = requests.post(API_URL, headers=headers, json=payload)
        if r.status_code == 200:
            filename = f"mockup_{int(time.time())}.jpg"
            with open(filename, "wb") as f: f.write(r.content)
            return filename
    except: pass
    return "https://placehold.co/800x450/111/00ff88.png?text=GEN+FAILED"

# --- 2. TEXT BRAIN ---
def generate_text(prompt):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": "llama-3.3-70b-versatile", "messages": [{"role": "system", "content": "Output ONLY JSON/HTML."}, {"role": "user", "content": prompt}]}
    try:
        r = requests.post(url, headers=headers, data=json.dumps(payload))
        if r.status_code == 200: return r.json()['choices'][0]['message']['content']
    except: pass
    return None

# --- 3. MANAGER: LOAD DATABASE ---
db = []
if os.path.exists(DB_FILE):
    try: with open(DB_FILE, "r") as f: db = json.load(f)
    except: db = []

# --- 4. FACTORY: CREATE PRODUCT ---
existing = [p['name'] for p in db]
res = generate_text(f"One unique B2B HTML Tool Idea not in: {existing}. Name Only.")
if not res: sys.exit(1)
new_name = re.sub(r'<[^>]+>', '', res.strip().replace('"', '')).strip()

if new_name in existing: 
    print("⚠️ Duplicate Idea. Skipping Production.")
    sys.exit(0)

print(f"🛠️ Building: {new_name}")
tool_raw = generate_text(f"Write HTML for '{new_name}'. Dark Theme. Single file. Output RAW HTML.")
tool_html = tool_raw.replace("```html", "").replace("```", "")
if "<!DOCTYPE" in tool_html: tool_html = tool_html[tool_html.find("<!DOCTYPE"):]
if "</html>" in tool_html: tool_html = tool_html[:tool_html.find("</html>")+7]

safe_name = re.sub(r'[^a-zA-Z0-9_]', '', new_name.replace(' ', '_')) + ".html"
with open(safe_name, "w") as f: f.write(tool_html)

print("🎨 Painting Image...")
img = generate_image(new_name)
price = random.choice(["49", "97", "149"])
link = f"https://www.paypal.com/cgi-bin/webscr?cmd=_xclick&business={os.environ.get('PAYPAL_EMAIL')}&item_name={urllib.parse.quote(new_name)}&amount={price}&currency_code=USD"

# --- 5. MANAGER: UPDATE RECORDS ---
db.insert(0, {"name": new_name, "desc": f"Automated Asset: {new_name}", "price": price, "file": safe_name, "image": img, "link": link})
with open(DB_FILE, "w") as f: json.dump(db, f, indent=2)

# --- 6. MANAGER: REBUILD SHOWROOM (WEBSITE) ---
html = """<!DOCTYPE html><html lang='en'><head><meta charset='UTF-8'><meta name='viewport' content='width=device-width, initial-scale=1.0'><title>DryPaper HQ</title><link href='https://fonts.googleapis.com/css2?family=Outfit:wght@300;600;800&display=swap' rel='stylesheet'><style>body{background:#050505;color:#fff;font-family:'Outfit',sans-serif;margin:0}.header{text-align:center;padding:80px 20px;background:radial-gradient(circle at top,#1a1a1a,#000)}.grid{max-width:1200px;margin:50px auto;display:grid;grid-template-columns:repeat(auto-fill,minmax(350px,1fr));gap:40px;padding:20px}.card{background:#111;border:1px solid #222;border-radius:16px;overflow:hidden;transition:0.3s}.card:hover{border-color:#00ff88;transform:translateY(-5px)}.card img{width:100%;height:220px;object-fit:cover}.info{padding:25px}.btn{display:block;background:#fff;color:#000;text-align:center;padding:12px;border-radius:50px;text-decoration:none;font-weight:bold;margin-top:20px}.btn:hover{background:#00ff88}</style></head><body><div class='header'><h1>DRYPAPER HQ</h1><p style='color:#666'>Elite Agency Tools</p></div><div class='grid'>"""
for item in db:
    html += f"<div class='card'><img src='{item['image']}'><div class='info'><h3>{item['name']}</h3><p style='color:#888'>{item['desc']}</p><div style='display:flex;justify-content:space-between;align-items:center'><span style='font-size:1.5em;font-weight:bold'>${item['price']}</span><a href='{item['file']}' class='btn'>GET ACCESS</a></div></div></div>"
html += "</div></body></html>"
with open(WEBSITE_FILE, "w") as f: f.write(html)

print("✅ Production & Maintenance Complete.")

