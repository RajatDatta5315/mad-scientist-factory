import requests, json, re, sys, os, random, time, urllib.parse
from email.utils import formatdate

print("--- 🏭 FACTORY: PREMIUM EDITION (MERCHANT + LOGO FIX) ---")

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
PAYPAL_EMAIL = os.environ.get("PAYPAL_EMAIL")
DB_FILE = "products.json"
WEBSITE_FILE = "index.html"
RSS_FILE = "feed.xml"

if not GROQ_API_KEY or not PAYPAL_EMAIL:
    print("❌ Secrets Missing.")
    sys.exit(1)

# --- LOAD DB & CHECK TIME LOCK ---
db = []
if os.path.exists(DB_FILE):
    try:
        with open(DB_FILE, "r") as f: 
            db = json.load(f)
    except:
        db = []

# Logic: One Product Per Week
current_time = int(time.time())
ONE_WEEK_SECONDS = 604800
should_generate = True

if db and len(db) > 0:
    last_product = db[0]
    last_created = last_product.get('timestamp', 0)
    if (current_time - last_created) < ONE_WEEK_SECONDS:
        print("🔒 LOCK ACTIVE. Refreshing site & feed only.")
        should_generate = False

# --- AI FUNCTIONS ---
def ask_ai(system_prompt, user_prompt):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": "llama-3.3-70b-versatile", "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]}
    try:
        r = requests.post(url, headers=headers, data=json.dumps(payload))
        if r.status_code == 200: return r.json()['choices'][0]['message']['content'].strip()
    except: pass
    return None

def generate_image(product_name, specific_vibe):
    filename = f"mockup_{int(time.time())}.jpg"
    prompt = urllib.parse.quote(f"high quality ui design of {product_name}, {specific_vibe}, dark mode, 8k")
    try:
        url = f"https://image.pollinations.ai/prompt/{prompt}?width=800&height=500&nologo=true&model=flux"
        r = requests.get(url)
        if r.status_code == 200:
            with open(filename, "wb") as f: f.write(r.content)
            return filename
    except: pass
    return "https://placehold.co/800x500.png"

# --- GENERATION ---
if should_generate:
    existing = [p['name'] for p in db]
    print("🕵️ Researching Trends...")
    name = ask_ai("Output ONLY name.", f"Suggest B2B SaaS Tool. NOT in: {existing}")
    name = re.sub(r'[^a-zA-Z0-9 ]', '', name).strip() if name else f"Tool_{int(time.time())}"
    
    tool_code = ask_ai("Output HTML.", f"Code tool: {name}. Dark Theme. Real Logic.")
    tool_code = tool_code.replace("```html", "").replace("```", "")
    safe_name = name.replace(" ", "_") + ".html"
    with open(safe_name, "w") as f: f.write(tool_code)
    
    img = generate_image(name, "dashboard")
    desc = ask_ai("Sales line.", f"Sell {name}.")
    price = random.choice(["29", "49"])
    
    file_url = f"https://www.drypaperhq.com/{safe_name}"
    link = f"https://www.paypal.com/cgi-bin/webscr?cmd=_xclick&business={PAYPAL_EMAIL}&item_name={name}&amount={price}&return={file_url}"
    
    db.insert(0, {"name": name, "desc": desc.replace('"', ''), "price": price, "file": safe_name, "image": img, "link": link, "timestamp": int(time.time())})
    with open(DB_FILE, "w") as f: json.dump(db, f, indent=2)

# --- WEBSITE UPDATE (WITH LOGO PNG & REAL ADDRESS) ---
print("🌐 Updating Storefront...")
html = """<!DOCTYPE html><html lang='en'><head><meta charset='UTF-8'><meta name='viewport' content='width=device-width, initial-scale=1.0'><title>DryPaper HQ</title>
<link rel="icon" type="image/png" href="favicon.png"> <link href='https://fonts.googleapis.com/css2?family=Outfit:wght@300;600;800&display=swap' rel='stylesheet'><style>body{background:#050505;color:#fff;font-family:'Outfit',sans-serif;margin:0}.header{text-align:center;padding:80px 20px;display:flex;flex-direction:column;align-items:center}.logo-img{width:80px;height:80px;border-radius:12px;margin-bottom:20px;border:2px solid #00ff88;box-shadow:0 0 20px rgba(0,255,136,0.2)}.header h1{font-size:3rem;margin:0;background:linear-gradient(to right,#fff,#888);-webkit-background-clip:text;-webkit-text-fill-color:transparent}.grid{max-width:1200px;margin:50px auto;display:grid;grid-template-columns:repeat(auto-fill,minmax(350px,1fr));gap:40px;padding:20px}.card{background:#0a0a0a;border:1px solid #222;border-radius:20px;overflow:hidden;transition:0.3s;display:flex;flex-direction:column}.card:hover{border-color:#00ff88;transform:translateY(-10px)}.card img{width:100%;height:220px;object-fit:cover;border-bottom:1px solid #222}.info{padding:25px;flex-grow:1;display:flex;flex-direction:column}.title{font-size:1.4rem;font-weight:bold;margin-bottom:10px}.desc{color:#888;font-size:0.9rem;margin-bottom:20px;line-height:1.5}.footer{margin-top:auto;display:flex;justify-content:space-between;align-items:center}.price{font-size:1.5rem;font-weight:800;color:#fff}.btn{background:#fff;color:#000;padding:10px 25px;border-radius:50px;text-decoration:none;font-weight:bold;transition:0.2s}.btn:hover{background:#00ff88;box-shadow:0 0 15px rgba(0,255,136,0.3)}.site-footer{text-align:center;padding:50px 20px;border-top:1px solid #222;color:#666;font-size:0.8rem;margin-top:50px}.site-footer a{color:#888;text-decoration:none;margin:0 10px}.site-footer p{margin:5px 0}</style></head><body>
<div class='header'>
    <img src='favicon.png' class='logo-img' alt='DryPaper Logo'> <h1>DRYPAPER HQ</h1>
    <p style='color:#666'>Premium Utility Assets for Agencies</p>
</div>
<div class='grid'>"""

for item in db:
    html += f"<div class='card'><img src='{item['image']}'><div class='info'><div class='title'>{item['name']}</div><div class='desc'>{item['desc']}</div><div class='footer'><div class='price'>${item['price']}</div><a href='{item['link']}' class='btn'>GET ACCESS</a></div></div></div>"

# FIXED: REAL ADDRESS FOR GOOGLE TRUST
html += """</div>
<div class='site-footer'>
    <p><strong>DryPaper HQ</strong></p>
    <p>S.K Gupta Road, Habra, West Bengal 743263, India</p>
    <p>Contact: drypaperofficial@gmail.com</p>
    <br>
    <p><a href='#'>Privacy Policy</a> | <a href='#'>Terms of Service</a> | <a href='#'>Refund Policy</a></p>
    <p>&copy; 2025 DryPaper Inc. All rights reserved.</p>
</div>
</body></html>"""

with open(WEBSITE_FILE, "w") as f: f.write(html)

# --- RSS FEED UPDATE ---
print("📡 Generating RSS Feed with Dates...")
rss = """<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0" xmlns:content="http://purl.org/rss/1.0/modules/content/" xmlns:dc="http://purl.org/dc/elements/1.1/">
<channel>
    <title>DryPaper HQ</title>
    <link>https://www.drypaperhq.com</link>
    <description>Premium AI Automation Tools</description>
    <language>en-us</language>
"""
for item in db[:15]:
    ts = item.get('timestamp', int(time.time()))
    pub_date = formatdate(ts)
    rss += f"""
    <item>
        <title>{item['name']}</title>
        <link>https://www.drypaperhq.com/{item.get('file', '')}</link>
        <guid>https://www.drypaperhq.com/{item.get('file', '')}</guid>
        <pubDate>{pub_date}</pubDate>
        <description>{item['desc']}</description>
        <content:encoded><![CDATA[<img src="https://www.drypaperhq.com/{item['image']}" /><p>{item['desc']}</p><p><strong>Price: ${item['price']}</strong></p><p><a href="{item['link']}">Get Access Now</a></p>]]></content:encoded>
    </item>"""
rss += "</channel></rss>"

with open(RSS_FILE, "w") as f: f.write(rss)
print("✅ Feed Fixed.")

