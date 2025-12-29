import requests, json, re, sys, os, random, time, urllib.parse, hashlib, string
from email.utils import formatdate

print("--- 🏭 FACTORY: SECURE + PREMIUM UI EDITION ---")

# --- SECRETS ---
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
PAYPAL_EMAIL = os.environ.get("PAYPAL_EMAIL")
# 🔥 PASSWORD IS NOW HIDDEN IN GITHUB SECRETS
VAULT_PASSWORD = os.environ.get("VAULT_PASSWORD") 

# --- SUPABASE CONFIG (Optional for now) ---
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

DB_FILE = "products.json"
WEBSITE_FILE = "index.html"
VAULT_FILE = "vault_secret.html"
RSS_FILE = "feed.xml"

if not GROQ_API_KEY or not PAYPAL_EMAIL or not VAULT_PASSWORD:
    print("❌ Critical Secrets (GROQ, PAYPAL, or VAULT_PASSWORD) Missing.")
    sys.exit(1)

# --- SECURITY UTILS ---
def generate_hash(text):
    return hashlib.sha256(text.encode()).hexdigest()

def random_string(length=8):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

VAULT_HASH = generate_hash(VAULT_PASSWORD)

# --- LOAD DB ---
db = []
if os.path.exists(DB_FILE):
    try:
        with open(DB_FILE, "r") as f: db = json.load(f)
    except: db = []

# Logic: Time Lock
current_time = int(time.time())
ONE_WEEK_SECONDS = 604800
should_generate = True

if db and len(db) > 0:
    last_created = db[0].get('timestamp', 0)
    if (current_time - last_created) < ONE_WEEK_SECONDS:
        print("🔒 LOCK ACTIVE. Refreshing site & feed only.")
        should_generate = False

# --- AI FUNCTIONS (Better Prompts) ---
def ask_ai(system_prompt, user_prompt):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": "llama-3.3-70b-versatile", "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]}
    try:
        r = requests.post(url, headers=headers, data=json.dumps(payload))
        if r.status_code == 200: return r.json()['choices'][0]['message']['content'].strip()
    except: pass
    return None

def get_image_url(product_name):
    # 1. Check if Manual Cover exists (manual_cover.jpg)
    if os.path.exists("manual_cover.jpg"):
        # Rename it to unique file to save it
        new_name = f"cover_{int(time.time())}.jpg"
        os.rename("manual_cover.jpg", new_name)
        return new_name
    
    # 2. Else Generate AI Image
    filename = f"mockup_{int(time.time())}.jpg"
    prompt = urllib.parse.quote(f"professional saas dashboard {product_name}, modern ui, dark mode, dribbble style, 4k")
    try:
        url = f"https://image.pollinations.ai/prompt/{prompt}?width=800&height=500&nologo=true&model=flux"
        r = requests.get(url)
        if r.status_code == 200:
            with open(filename, "wb") as f: f.write(r.content)
            return filename
    except: pass
    return "https://placehold.co/800x500/000000/FFFFFF/png?text=Premium+Tool"

# --- GENERATION ---
if should_generate:
    existing = [p['name'] for p in db]
    print("🕵️ Researching Premium Trends...")
    name = ask_ai("Output ONLY name.", f"Suggest High-Ticket B2B Micro-SaaS. NOT in: {existing}")
    name = re.sub(r'[^a-zA-Z0-9 ]', '', name).strip() if name else f"Tool_{int(time.time())}"
    
    secure_id = random_string(10)
    safe_name = f"Tool_{secure_id}.html"
    
    # 🔥 PREMIUM UI PROMPT (Tailwind)
    print("💎 Coding Premium UI...")
    tool_code = ask_ai("Output HTML only.", f"Create a Single-Page App: {name}. Use Tailwind CSS via CDN. Dark/Cyberpunk Theme. Professional UI. Fully functional Logic (JS). No placeholder text.")
    tool_code = tool_code.replace("```html", "").replace("```", "")
    with open(safe_name, "w") as f: f.write(tool_code)
    
    img = get_image_url(name)
    desc = ask_ai("Sales line.", f"Write a punchy 1-liner selling {name} to agency owners.")
    price = random.choice(["49", "97"]) # Higher Price for Premium
    
    file_url = f"https://www.drypaperhq.com/{safe_name}"
    link = f"https://www.paypal.com/cgi-bin/webscr?cmd=_xclick&business={PAYPAL_EMAIL}&item_name={name}&amount={price}&return={file_url}"
    
    # New Product Object
    new_prod = {"name": name, "desc": desc.replace('"', ''), "price": price, "file": safe_name, "image": img, "link": link, "timestamp": int(time.time())}
    db.insert(0, new_prod)
    with open(DB_FILE, "w") as f: json.dump(db, f, indent=2)

    # --- SUPABASE SYNC (Send to Nehira) ---
    if SUPABASE_URL and SUPABASE_KEY:
        try:
            print("🚀 Syncing with KRYV/Nehira...")
            headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}
            # Assuming table name is 'drypaper_inventory'
            requests.post(f"{SUPABASE_URL}/rest/v1/drypaper_inventory", headers=headers, data=json.dumps(new_prod))
        except: print("⚠️ Supabase Sync Failed (Check Secrets)")

# --- WEBSITE UPDATE ---
print("🌐 Updating Storefront...")
html = """<!DOCTYPE html><html lang='en'><head><meta charset='UTF-8'><meta name='viewport' content='width=device-width, initial-scale=1.0'><title>DryPaper HQ</title>
<link rel="icon" type="image/png" href="Favicon.png">
<script src="https://cdn.tailwindcss.com"></script>
<link href='https://fonts.googleapis.com/css2?family=Outfit:wght@300;600;800&display=swap' rel='stylesheet'>
<style>body{font-family:'Outfit',sans-serif; background-color:#050505; color:white;}</style>
</head><body>
<div class='flex flex-col items-center py-20 px-5 text-center'>
    <img src='Favicon.png' class='w-20 h-20 rounded-xl mb-5 border-2 border-green-400 shadow-[0_0_20px_rgba(74,222,128,0.2)]'>
    <h1 class='text-5xl font-extrabold bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-500 mb-2'>DRYPAPER HQ</h1>
    <p class='text-gray-400'>Elite Automation Assets for Agencies</p>
</div>
<div class='max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-10 p-5'>"""

for item in db:
    html += f"""
    <div class='bg-neutral-900 border border-neutral-800 rounded-2xl overflow-hidden hover:border-green-400 transition transform hover:-translate-y-2 flex flex-col'>
        <img src='{item['image']}' class='w-full h-56 object-cover border-b border-neutral-800'>
        <div class='p-6 flex-grow flex flex-col'>
            <div class='text-2xl font-bold mb-2'>{item['name']}</div>
            <div class='text-gray-400 text-sm mb-5 leading-relaxed'>{item['desc']}</div>
            <div class='mt-auto flex justify-between items-center'>
                <div class='text-2xl font-extrabold text-white'>${item['price']}</div>
                <a href='{item['link']}' class='bg-white text-black px-6 py-2 rounded-full font-bold hover:bg-green-400 hover:shadow-[0_0_15px_rgba(74,222,128,0.4)] transition'>GET ACCESS</a>
            </div>
        </div>
    </div>"""

html += """</div>
<div class='text-center py-10 border-t border-neutral-800 text-gray-500 text-sm mt-10'>
    <p class='font-bold text-white mb-2'>DryPaper HQ</p>
    <p>S.K Gupta Road, Habra, West Bengal 743263, India</p>
    <p>Contact: drypaperofficial@gmail.com</p>
    <div class='mt-4 space-x-4'>
        <a href='#' class='hover:text-white'>Privacy</a>
        <a href='#' class='hover:text-white'>Terms</a>
    </div>
    <p class='mt-4'>&copy; 2025 DryPaper Inc.</p>
</div>
</body></html>"""

with open(WEBSITE_FILE, "w") as f: f.write(html)

# --- SECURE VAULT UPDATE (HASHED) ---
print("🔐 Updating Secure Vault...")
vault_html = f"""<!DOCTYPE html><html><head><title>Founder Vault</title>
<script src="https://cdn.tailwindcss.com"></script>
<script>
async function sha256(message) {{
    const msgBuffer = new TextEncoder().encode(message);
    const hashBuffer = await crypto.subtle.digest('SHA-256', msgBuffer);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
}}
async function check() {{
    var p = prompt("ENTER ACCESS CODE:");
    var h = await sha256(p);
    if(h === "{VAULT_HASH}"){{ document.getElementById('content').classList.remove('hidden'); }} 
    else {{ alert("ACCESS DENIED"); window.location.href='https://google.com'; }}
}}
</script>
</head><body onload="check()" class="bg-black text-green-500 font-mono p-10">
<div id='content' class='hidden'>
    <h1 class="text-3xl mb-10 border-b border-green-900 pb-4">DRYPAPER ASSET VAULT (SECURE)</h1>
    <div class="space-y-4">"""

for item in db:
    vault_html += f"<a href='{item.get('file', '#')}' target='_blank' class='block p-4 border border-green-900 hover:bg-green-900/20 transition'>{item['name']} <span class='float-right'>[OPEN]</span></a>"

vault_html += "</div></div></body></html>"
with open(VAULT_FILE, "w") as f: f.write(vault_html)

# --- RSS ---
rss = """<?xml version="1.0" ?><rss version="2.0"><channel><title>DryPaper HQ</title><link>https://www.drypaperhq.com</link><description>Tools</description>"""
for item in db[:15]:
    rss += f"<item><title>{item['name']}</title><link>https://www.drypaperhq.com/{item.get('file', '')}</link><description>{item['desc']}</description></item>"
rss += "</channel></rss>"
with open(RSS_FILE, "w") as f: f.write(rss)
print("✅ Factory Complete.")

