import requests, json, re, sys, os, random, time, urllib.parse, hashlib, string
from email.utils import formatdate

print("--- 🏭 FACTORY: SUPABASE CONNECTED ---")

# --- SECRETS ---
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
PAYPAL_EMAIL = os.environ.get("PAYPAL_EMAIL")
VAULT_PASSWORD = os.environ.get("VAULT_PASSWORD") 

# --- NEW: SUPABASE SECRETS ---
# (Ye tujhe Github Secrets mein daalne honge)
SUPABASE_URL = os.environ.get("NEXT_PUBLIC_SUPABASE_URL") 
SUPABASE_KEY = os.environ.get("NEXT_PUBLIC_SUPABASE_ANON_KEY")

DB_FILE = "products.json"

if not GROQ_API_KEY or not PAYPAL_EMAIL:
    print("❌ Critical Secrets Missing.")
    sys.exit(1)

# --- LOAD DB ---
db = []
if os.path.exists(DB_FILE):
    try:
        with open(DB_FILE, "r") as f: db = json.load(f)
    except: db = []

# Logic: Time Lock (Same as before)
current_time = int(time.time())
ONE_WEEK_SECONDS = 604800
should_generate = True

if db and len(db) > 0:
    last_created = db[0].get('timestamp', 0)
    if (current_time - last_created) < ONE_WEEK_SECONDS:
        print("🔒 LOCK ACTIVE. Skipping Generation.")
        should_generate = False

# --- AI & IMAGE FUNCTIONS ---
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
    # Try Manual Cover
    if os.path.exists("manual_cover.jpg"):
        new_name = f"cover_{int(time.time())}.jpg"
        os.rename("manual_cover.jpg", new_name)
        # Upload to Supabase Storage logic can be added here, but for now we keep local
        return "https://placehold.co/800x500/000000/FFFFFF/png?text=Manual+Cover" 
    
    # Generate AI Image
    prompt = urllib.parse.quote(f"futuristic ui dashboard {product_name}, cyberpunk style, dark mode, high tech")
    return f"https://image.pollinations.ai/prompt/{prompt}?width=800&height=500&nologo=true&model=flux"

# --- GENERATION ---
if should_generate:
    existing = [p['name'] for p in db]
    print("🕵️ Researching Premium Trends...")
    name = ask_ai("Output ONLY name.", f"Suggest High-Ticket AI Tool. NOT in: {existing}")
    name = re.sub(r'[^a-zA-Z0-9 ]', '', name).strip() if name else f"Tool_{int(time.time())}"
    
    secure_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    safe_name = f"Tool_{secure_id}.html"
    
    print("💎 Coding Premium UI...")
    tool_code = ask_ai("Output HTML only.", f"Create Single-Page App: {name}. Dark Cyberpunk Theme. Tailwind CSS.")
    tool_code = tool_code.replace("```html", "").replace("```", "")
    with open(safe_name, "w") as f: f.write(tool_code)
    
    img = get_image_url(name)
    desc = ask_ai("Sales line.", f"Write 2 sentence description for {name}.")
    price = random.choice(["49", "97"])
    
    file_url = f"https://www.drypaperhq.com/{safe_name}" # Old Method
    link = f"https://www.paypal.com/cgi-bin/webscr?cmd=_xclick&business={PAYPAL_EMAIL}&item_name={name}&amount={price}&return={file_url}"
    
    # New Product Object
    new_prod = {
        "name": name, 
        "description": desc.replace('"', ''), 
        "price": float(price), 
        "link": link, # PayPal Link
        "image_url": img,
        "status": "active"
    }
    
    # Save to JSON (Backup)
    db.insert(0, new_prod)
    with open(DB_FILE, "w") as f: json.dump(db, f, indent=2)

    # --- 🔥 SUPABASE INJECTION (The Bridge) ---
    if SUPABASE_URL and SUPABASE_KEY:
        try:
            print("🚀 Injecting into DryPaper Store...")
            headers = {
                "apikey": SUPABASE_KEY, 
                "Authorization": f"Bearer {SUPABASE_KEY}", 
                "Content-Type": "application/json",
                "Prefer": "return=minimal"
            }
            # Insert into 'drypaper_assets' table
            r = requests.post(f"{SUPABASE_URL}/rest/v1/drypaper_assets", headers=headers, data=json.dumps(new_prod))
            if r.status_code == 201:
                print("✅ Successfully Listed on Store!")
            else:
                print(f"⚠️ Store Injection Failed: {r.text}")
        except Exception as e: 
            print(f"⚠️ Sync Error: {e}")

print("✅ Factory Operation Complete.")

