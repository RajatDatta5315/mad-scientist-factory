import requests, json, re, sys, os, random, time, urllib.parse

print("--- 🏭 FACTORY: PREMIUM EDITION (PAYWALL & SMART IMAGES) ---")

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
HF_TOKEN = os.environ.get("HF_TOKEN")
PAYPAL_EMAIL = os.environ.get("PAYPAL_EMAIL")
DB_FILE = "products.json"
WEBSITE_FILE = "index.html"

if not GROQ_API_KEY or not PAYPAL_EMAIL:
    print("❌ Critical: Secrets Missing (GROQ or PAYPAL).")
    sys.exit(1)

# --- 1. SMART IMAGE GENERATOR (Retry Logic + Better Prompts) ---
def generate_image(product_name, specific_prompt):
    if not HF_TOKEN: 
        print("⚠️ HF_TOKEN missing in Secrets.")
        return "FAILED_NO_TOKEN"
    
    API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    
    # AI ne jo prompt diya usko use karenge
    full_prompt = f"high quality ui design, {specific_prompt}, 8k, unreal engine 5, behance top project, dark mode, neon accents, futuristic, detailed"
    
    payload = {"inputs": full_prompt}
    
    # 3 Retries in case of Server Busy
    for i in range(3):
        try:
            r = requests.post(API_URL, headers=headers, json=payload)
            if r.status_code == 200:
                filename = f"mockup_{int(time.time())}.jpg"
                with open(filename, "wb") as f: f.write(r.content)
                print("✅ Image Generated Successfully")
                return filename
            else:
                print(f"⚠️ Image Gen Attempt {i+1} Failed: {r.status_code}")
                time.sleep(5) # Wait 5 sec before retry
        except: pass
    
    return "FAILED_API_ERROR"

# --- 2. TEXT BRAIN (AI) ---
def generate_text(prompt):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": "llama-3.3-70b-versatile", "messages": [{"role": "system", "content": "Output ONLY raw text/code. No yapping."}, {"role": "user", "content": prompt}]}
    try:
        r = requests.post(url, headers=headers, data=json.dumps(payload))
        if r.status_code == 200: return r.json()['choices'][0]['message']['content']
    except: pass
    return None

# --- 3. LOAD DATABASE ---
db = []
if os.path.exists(DB_FILE):
    try:
        with open(DB_FILE, "r") as f: db = json.load(f)
    except: db = []

# --- 4. CREATE NEW PRODUCT ---
existing = [p['name'] for p in db]
res = generate_text(f"Generate 1 Unique High-Ticket B2B HTML Tool Idea NOT in this list: {existing}. Return ONLY the Product Name.")
if not res: sys.exit(1)
new_name = re.sub(r'<[^>]+>', '', res.strip().replace('"', '')).strip()

if new_name in existing:
    print("⚠️ Duplicate Idea. Skipping.")
    sys.exit(0)

print(f"🛠️ Developing: {new_name}")

# Generate HTML Tool
tool_raw = generate_text(f"Write a single-file Premium HTML Tool for '{new_name}'. Dark Modern Theme. Fully functional JavaScript. Inline CSS. No external dependencies. Output RAW HTML.")
tool_html = tool_raw.replace("```html", "").replace("```", "")
if "<!DOCTYPE" in tool_html: tool_html = tool_html[tool_html.find("<!DOCTYPE"):]
if "</html>" in tool_html: tool_html = tool_html[:tool_html.find("</html>")+7]

safe_name = re.sub(r'[^a-zA-Z0-9_]', '', new_name.replace(' ', '_')) + ".html"
with open(safe_name, "w") as f: f.write(tool_html)

# Generate Specific Image Prompt
print("🎨 Designing Mockup...")
visual_desc = generate_text(f"Describe the UI dashboard of '{new_name}' in 10 words for an image generator. Mention charts, colors, and layout.")
img = generate_image(new_name, visual_desc)

# Generate SEO/Sales Copy
desc = generate_text(f"Write a 2-sentence catchy sales description for '{new_name}'.")

# Pricing & PayPal Link
price = random.choice(["49", "97", "149"])
# 🔥 FIX: Link goes to PayPal, NOT the file
link = f"https://www.paypal.com/cgi-bin/webscr?cmd=_xclick&business={PAYPAL_EMAIL}&item_name={urllib.parse.quote(new_name)}&amount={price}&currency_code=USD"

# --- 5. VALIDATION & SAVE (The Filter) ---
# Agar image fail hui, to product DB mein add hi mat karo. Store saaf rahega.
if "FAILED" in img:
    print("❌ Image Generation Failed. Discarding product to keep store clean.")
    os.remove(safe_name) # Delete the HTML file too
else:
    # Add to DB (Newest First)
    db.insert(0, {
        "name": new_name, 
        "desc": desc.replace('"', ''), 
        "price": price, 
        "file": safe_name, 
        "image": img, 
        "link": link # PayPal Link
    })
    
    # Save DB
    with open(DB_FILE, "w") as f: json.dump(db, f, indent=2)
    print(f"✅ Product '{new_name}' added to inventory.")

# --- 6. REBUILD WEBSITE (Persistence Guaranteed) ---
print("🌐 Updating Website...")
html = """<!DOCTYPE html><html lang='en'><head><meta charset='UTF-8'><meta name='viewport' content='width=device-width, initial-scale=1.0'><title>DryPaper HQ</title><link href='https://fonts.googleapis.com/css2?family=Outfit:wght@300;600;800&display=swap' rel='stylesheet'><style>body{background:#050505;color:#fff;font-family:'Outfit',sans-serif;margin:0}.header{text-align:center;padding:80px 20px;background:radial-gradient(circle at top,#1a1a1a,#000)}.header h1{font-size:3rem;margin:0;background:linear-gradient(to right,#fff,#888);-webkit-background-clip:text;-webkit-text-fill-color:transparent}.grid{max-width:1200px;margin:50px auto;display:grid;grid-template-columns:repeat(auto-fill,minmax(350px,1fr));gap:40px;padding:20px}.card{background:#111;border:1px solid #222;border-radius:16px;overflow:hidden;transition:0.3s;display:flex;flex-direction:column}.card:hover{border-color:#00ff88;transform:translateY(-5px)}.card img{width:100%;height:220px;object-fit:cover}.info{padding:25px;flex-grow:1;display:flex;flex-direction:column}.title{font-size:1.4rem;font-weight:bold;margin-bottom:10px}.desc{color:#888;font-size:0.9rem;margin-bottom:20px;line-height:1.5}.footer{margin-top:auto;display:flex;justify-content:space-between;align-items:center}.price{font-size:1.5rem;font-weight:bold;color:#fff}.btn{background:#fff;color:#000;padding:10px 25px;border-radius:50px;text-decoration:none;font-weight:bold;transition:0.2s}.btn:hover{background:#00ff88;box-shadow:0 0 15px rgba(0,255,136,0.4)}</style></head><body><div class='header'><h1>DRYPAPER HQ</h1><p style='color:#666'>Elite Agency Tools</p></div><div class='grid'>"""

# Loop through ALL products in DB
for item in db:
    # Double check: Don't show failed items if any slipped through
    if "FAILED" not in item['image']:
        html += f"""
        <div class='card'>
            <img src='{item['image']}' alt='{item['name']}'>
            <div class='info'>
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

print("✅ Website Rebuilt Successfully.")

