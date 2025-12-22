import requests, json, re, sys, os, random, time, urllib.parse

print("--- 🏭 FACTORY: MARKET RESEARCH SNIPER (AUTO-REDIRECT) ---")

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
HF_TOKEN = os.environ.get("HF_TOKEN")
PAYPAL_EMAIL = os.environ.get("PAYPAL_EMAIL")
DB_FILE = "products.json"
WEBSITE_FILE = "index.html"

if not GROQ_API_KEY or not PAYPAL_EMAIL:
    print("❌ Secrets Missing.")
    sys.exit(1)

# --- 1. THE BRAIN (LLAMA 3) ---
def ask_ai(system_prompt, user_prompt):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.7
    }
    try:
        r = requests.post(url, headers=headers, data=json.dumps(payload))
        if r.status_code == 200:
            return r.json()['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"⚠️ AI Error: {e}")
    return None

# --- 2. IMAGE GENERATOR ---
def generate_image(product_name):
    filename = f"mockup_{int(time.time())}.jpg"
    print("🎨 Generating UI Mockup...")
    try:
        prompt = f"futuristic dark ui dashboard for {product_name} software, neon green charts, analytics, high quality, 8k render"
        encoded = urllib.parse.quote(prompt)
        url = f"https://image.pollinations.ai/prompt/{encoded}?width=800&height=450&nologo=true&model=flux"
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            with open(filename, "wb") as f: f.write(r.content)
            return filename
    except: pass
    return "https://placehold.co/800x450/000/0f0.png?text=Tool+Preview"

# --- 3. LOAD DATABASE ---
db = []
if os.path.exists(DB_FILE):
    try: with open(DB_FILE, "r") as f: db = json.load(f)
    except: db = []

# --- 4. STEP 1: MARKET RESEARCH ---
existing_tools = [p['name'] for p in db]
print("🕵️ Doing Market Research...")

research_prompt = f"""
You are a Product Manager. Analyze market needs for Agencies.
Select ONE High-Value Micro-Tool idea (Calculator, Generator, Converter) buildable in single HTML/JS.
CONSTRAINT:
- DO NOT use: {existing_tools}
- Output ONLY tool name (Max 4 words). No description.
"""
new_name = ask_ai("Output ONLY the name.", research_prompt)

if not new_name or len(new_name) > 50 or "\n" in new_name:
    print(f"⚠️ AI Hallucinated. Using Backup.")
    new_name = f"Agency_ROI_Calculator_{int(time.time())}"
else:
    new_name = re.sub(r'[^a-zA-Z0-9 ]', '', new_name).strip()

print(f"💎 Winning Idea: {new_name}")

# --- 5. STEP 2: BUILD TOOL ---
print("🏗️ Engineering Code...")
code_prompt = f"""
Act as Senior Dev. Write complete code for '{new_name}'.
Theme: Cyberpunk Dark Mode.
REQUIREMENTS:
1. Single HTML file (CSS/JS inside).
2. MUST BE FUNCTIONAL (Logic must work).
3. Professional UI.
4. No external APIs.
Output ONLY RAW HTML.
"""
tool_code = ask_ai("Output ONLY HTML code.", code_prompt)

if not tool_code or "<html" not in tool_code:
    print("❌ Code Gen Failed.")
    sys.exit(1)

tool_code = tool_code.replace("```html", "").replace("```", "")
safe_filename = new_name.replace(" ", "_") + ".html"
with open(safe_filename, "w") as f: f.write(tool_code)

# --- 6. STEP 3: PACKAGING (WITH REDIRECT) ---
img = generate_image(new_name)
desc = ask_ai("Write 1 punchy sales sentence.", f"Sell {new_name}.")
price = random.choice(["29", "49", "67"])

# 🔥 THE MAGIC FIX: Redirect to File after payment
file_url = f"https://www.drypaperhq.com/{safe_filename}"
link = f"https://www.paypal.com/cgi-bin/webscr?cmd=_xclick&business={PAYPAL_EMAIL}&item_name={urllib.parse.quote(new_name)}&amount={price}&currency_code=USD&return={urllib.parse.quote(file_url)}"

# --- 7. SAVE ---
db.insert(0, {"name": new_name, "desc": desc.replace('"', ''), "price": price, "file": safe_filename, "image": img, "link": link})
with open(DB_FILE, "w") as f: json.dump(db, f, indent=2)

# --- 8. UPDATE WEBSITE ---
print("🌐 Updating Showroom...")
html = """<!DOCTYPE html><html lang='en'><head><meta charset='UTF-8'><meta name='viewport' content='width=device-width, initial-scale=1.0'><title>DryPaper HQ</title><link href='https://fonts.googleapis.com/css2?family=Outfit:wght@300;600;800&display=swap' rel='stylesheet'><style>body{background:#050505;color:#fff;font-family:'Outfit',sans-serif;margin:0}.header{text-align:center;padding:100px 20px}.header h1{font-size:3rem;margin-bottom:10px;background:linear-gradient(to right,#fff,#888);-webkit-background-clip:text;-webkit-text-fill-color:transparent}.grid{max-width:1200px;margin:50px auto;display:grid;grid-template-columns:repeat(auto-fill,minmax(350px,1fr));gap:40px;padding:20px}.card{background:#0a0a0a;border:1px solid #222;border-radius:20px;overflow:hidden;transition:0.3s;display:flex;flex-direction:column}.card:hover{border-color:#00ff88;transform:translateY(-10px)}.card img{width:100%;height:220px;object-fit:cover;border-bottom:1px solid #222}.info{padding:25px;flex-grow:1;display:flex;flex-direction:column}.title{font-size:1.4rem;font-weight:bold;margin-bottom:10px}.desc{color:#888;font-size:0.9rem;margin-bottom:20px;line-height:1.5}.footer{margin-top:auto;display:flex;justify-content:space-between;align-items:center}.price{font-size:1.5rem;font-weight:800;color:#fff}.btn{background:#fff;color:#000;padding:10px 25px;border-radius:50px;text-decoration:none;font-weight:bold;transition:0.2s}.btn:hover{background:#00ff88;box-shadow:0 0 15px rgba(0,255,136,0.3)}</style></head><body><div class='header'><h1>DRYPAPER HQ</h1><p style='color:#666'>Premium Utility Assets</p></div><div class='grid'>"""
for item in db:
    html += f"<div class='card'><img src='{item['image']}'><div class='info'><div class='title'>{item['name']}</div><div class='desc'>{item['desc']}</div><div class='footer'><div class='price'>${item['price']}</div><a href='{item['link']}' class='btn'>GET ACCESS</a></div></div></div>"
html += "</div></body></html>"
with open(WEBSITE_FILE, "w") as f: f.write(html)

print("✅ Mission Accomplished: Tool Deployed & Payment Linked.")

