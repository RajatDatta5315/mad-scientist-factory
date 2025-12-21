import requests, json, re, sys, os, random, time, urllib.parse

print("--- 🏭 FACTORY: FUNCTIONAL TOOLS (NO SYNTAX ERRORS) ---")

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
HF_TOKEN = os.environ.get("HF_TOKEN")
PAYPAL_EMAIL = os.environ.get("PAYPAL_EMAIL")
DB_FILE = "products.json"
WEBSITE_FILE = "index.html"

if not GROQ_API_KEY or not PAYPAL_EMAIL:
    print("❌ Secrets Missing.")
    sys.exit(1)

# --- 1. IMAGE GENERATOR (Reliable) ---
def generate_image(product_name, specific_prompt):
    filename = f"mockup_{int(time.time())}.jpg"
    
    # Try Hugging Face
    if HF_TOKEN:
        try:
            API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
            headers = {"Authorization": f"Bearer {HF_TOKEN}"}
            payload = {"inputs": f"dashboard UI for {product_name}, {specific_prompt}, dark mode, neon green charts, high quality, 8k, no text"}
            r = requests.post(API_URL, headers=headers, json=payload)
            if r.status_code == 200:
                with open(filename, "wb") as f: f.write(r.content)
                return filename
        except: pass
    
    # Backup: Pollinations (No Logo)
    try:
        encoded = urllib.parse.quote(f"futuristic dark software interface {product_name} {specific_prompt}")
        url = f"https://image.pollinations.ai/prompt/{encoded}?width=800&height=450&nologo=true&model=flux"
        r = requests.get(url, timeout=10)
        with open(filename, "wb") as f: f.write(r.content)
        return filename
    except: pass
    
    # Last Resort
    return f"https://placehold.co/800x450/000/0f0.png?text={urllib.parse.quote(product_name)}"

# --- 2. TEXT BRAIN ---
def generate_text(prompt):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": "llama-3.3-70b-versatile", "messages": [{"role": "system", "content": "Output ONLY raw code/text."}, {"role": "user", "content": prompt}]}
    try:
        r = requests.post(url, headers=headers, data=json.dumps(payload))
        if r.status_code == 200: return r.json()['choices'][0]['message']['content']
    except: pass
    return "Tool"

# --- 3. LOAD DB (FIXED PROPERLY) ---
db = []
if os.path.exists(DB_FILE):
    try:
        with open(DB_FILE, "r") as f:
            db = json.load(f)
    except:
        db = []

# --- 4. CREATE FUNCTIONAL TOOL ---
existing = [p['name'] for p in db]
# AI ko bol rahe hain ki sirf WORKING JS TOOLS banaye
res = generate_text(f"Idea for a B2B HTML Utility Tool (Calculator, Generator, Auditor, Converter) that works 100% in browser JS. NOT 'AI Writer'. Name Only. Not in: {existing}")
if not res: sys.exit(1)
new_name = re.sub(r'<[^>]+>', '', res.strip().replace('"', '')).strip()
if new_name in existing: sys.exit(0)

print(f"🛠️ Building Functional Tool: {new_name}")

# Generate Code
prompt = f"""
Write a single-file HTML/JS tool called '{new_name}'.
Theme: Dark Mode, Neon Green Accents.
REQUIREMENTS:
1. MUST BE FULLY FUNCTIONAL using JavaScript.
2. If it's a calculator, it must calculate.
3. If it's a generator, it must generate results/text.
4. NO fake buttons. NO 'API Error' alerts.
5. Inline CSS/JS.
Output ONLY RAW HTML.
"""
tool_raw = generate_text(prompt)
tool_html = tool_raw.replace("```html", "").replace("```", "")
if "<!DOCTYPE" in tool_html: tool_html = tool_html[tool_html.find("<!DOCTYPE"):]
if "</html>" in tool_html: tool_html = tool_html[:tool_html.find("</html>")+7]

safe_name = re.sub(r'[^a-zA-Z0-9_]', '', new_name.replace(' ', '_')) + ".html"
with open(safe_name, "w") as f: f.write(tool_html)

# Image & Data
visual_desc = generate_text(f"UI keywords for {new_name}")
img = generate_image(new_name, visual_desc)
desc = generate_text(f"2-sentence sales copy for {new_name}")
price = random.choice(["27", "47", "67"]) 
link = f"https://www.paypal.com/cgi-bin/webscr?cmd=_xclick&business={PAYPAL_EMAIL}&item_name={urllib.parse.quote(new_name)}&amount={price}&currency_code=USD"

# --- 5. SAVE ---
db.insert(0, {"name": new_name, "desc": desc.replace('"',''), "price": price, "file": safe_name, "image": img, "link": link})
with open(DB_FILE, "w") as f: json.dump(db, f, indent=2)

# --- 6. WEBSITE UPDATE ---
html = """<!DOCTYPE html><html lang='en'><head><meta charset='UTF-8'><meta name='viewport' content='width=device-width, initial-scale=1.0'><title>DryPaper HQ</title><link href='https://fonts.googleapis.com/css2?family=Outfit:wght@300;600;800&display=swap' rel='stylesheet'><style>body{background:#050505;color:#fff;font-family:'Outfit',sans-serif;margin:0}.header{text-align:center;padding:100px 20px}.grid{max-width:1200px;margin:50px auto;display:grid;grid-template-columns:repeat(auto-fill,minmax(350px,1fr));gap:40px;padding:20px}.card{background:#0a0a0a;border:1px solid #222;border-radius:20px;overflow:hidden;transition:0.3s}.card:hover{border-color:#00ff88;transform:translateY(-10px)}.card img{width:100%;height:220px;object-fit:cover}.info{padding:30px}.title{font-size:1.5rem;font-weight:bold}.price{font-size:1.5rem;font-weight:800;color:#fff}.btn{display:inline-block;background:#fff;color:#000;padding:10px 30px;border-radius:50px;text-decoration:none;font-weight:bold;margin-top:20px}.btn:hover{background:#00ff88}</style></head><body><div class='header'><h1>DRYPAPER HQ</h1><p>Functional Assets for Agencies</p></div><div class='grid'>"""
for item in db:
    html += f"<div class='card'><img src='{item['image']}'><div class='info'><div class='title'>{item['name']}</div><p>{item['desc']}</p><div style='display:flex;justify-content:space-between;align-items:center'><div class='price'>${item['price']}</div><a href='{item['link']}' class='btn'>GET ACCESS</a></div></div></div>"
html += "</div></body></html>"
with open(WEBSITE_FILE, "w") as f: f.write(html)

print("✅ Factory Done (Fixed).")

