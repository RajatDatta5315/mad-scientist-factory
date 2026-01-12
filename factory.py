import requests, json, re, sys, os, random, time, urllib.parse, hashlib, string

print("--- 🏭 FACTORY: FULL CLOUD AUTOMATION ---")

# --- SECRETS ---
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
PAYPAL_EMAIL = os.environ.get("PAYPAL_EMAIL")
SUPABASE_URL = os.environ.get("NEXT_PUBLIC_SUPABASE_URL") 
SUPABASE_KEY = os.environ.get("NEXT_PUBLIC_SUPABASE_ANON_KEY")

DB_FILE = "products.json"

if not GROQ_API_KEY or not PAYPAL_EMAIL or not SUPABASE_URL:
    print("❌ Critical Secrets Missing.")
    sys.exit(1)

# --- LOAD DB ---
db = []
if os.path.exists(DB_FILE):
    try:
        with open(DB_FILE, "r") as f: db = json.load(f)
    except: db = []

# --- FUNCTIONS ---
def ask_ai(system_prompt, user_prompt):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": "llama-3.3-70b-versatile", "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]}
    try:
        r = requests.post(url, headers=headers, data=json.dumps(payload))
        if r.status_code == 200: return r.json()['choices'][0]['message']['content'].strip()
    except: pass
    return None

def upload_to_supabase(filename, bucket):
    """Uploads a local file to Supabase Storage and returns Public URL"""
    try:
        with open(filename, 'rb') as f:
            file_data = f.read()
        
        # Upload
        url = f"{SUPABASE_URL}/storage/v1/object/{bucket}/{filename}"
        headers = {"Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "text/html" if filename.endswith(".html") else "image/jpeg"}
        r = requests.post(url, headers=headers, data=file_data)
        
        # Get Public URL
        public_url = f"{SUPABASE_URL}/storage/v1/object/public/{bucket}/{filename}"
        print(f"☁️ Uploaded {filename} to {bucket}")
        return public_url
    except Exception as e:
        print(f"❌ Upload Error: {e}")
        return None

# --- GENERATION ---
# Check Time Lock (12 Hours for Testing, change to 604800 for week)
current_time = int(time.time())
if db and (current_time - db[0].get('timestamp', 0)) < 43200: 
    print("⏳ Waiting for cooldown...")
    # Uncomment next line to force run:
    # pass 
else:
    print("🚀 Starting Production Cycle...")
    
    # 1. IDEA
    existing = [p['name'] for p in db]
    name = ask_ai("Output ONLY name.", f"Suggest a specialized AI Micro-Tool for agencies. NOT in: {existing}")
    name = re.sub(r'[^a-zA-Z0-9 ]', '', name).strip() if name else f"Tool_{int(time.time())}"
    
    # 2. CODE (The Product)
    safe_name = f"tool_{int(time.time())}.html"
    print(f"💎 Coding {name}...")
    tool_code = ask_ai("Output HTML only.", f"Create Single-Page App: {name}. Dark Theme. Tailwind CSS. Fully functional.")
    tool_code = tool_code.replace("```html", "").replace("```", "")
    with open(safe_name, "w") as f: f.write(tool_code)
    
    # 3. UPLOAD PRODUCT TO CLOUD
    product_download_url = upload_to_supabase(safe_name, "product-files")
    
    if not product_download_url:
        print("❌ Failed to upload product. Aborting.")
        sys.exit(1)

    # 4. MARKETING ASSETS
    desc = ask_ai("Sales line.", f"Write 1 sentence description for {name}.")
    price = random.choice(["29", "49", "97"])
    
    # 5. COVER IMAGE
    # (Agar manual_cover.jpg hai to wo use karo, nahi to AI)
    if os.path.exists("manual_cover.jpg"):
        cover_name = f"cover_{int(time.time())}.jpg"
        os.rename("manual_cover.jpg", cover_name)
        img_url = upload_to_supabase(cover_name, "product-images")
    else:
        # Fallback AI Image
        prompt = urllib.parse.quote(f"ui interface {name} dark mode cyberpunk")
        img_url = f"https://image.pollinations.ai/prompt/{prompt}?width=800&height=500&nologo=true"

    # 6. PAYPAL LINK GENERATOR
    # User pays -> PayPal redirects to 'product_download_url' (The Supabase file link)
    paypal_link = f"https://www.paypal.com/cgi-bin/webscr?cmd=_xclick&business={PAYPAL_EMAIL}&item_name={name}&amount={price}&return={product_download_url}"

    # 7. SAVE TO DB & STORE
    new_prod = {
        "name": name, 
        "description": desc.replace('"', ''), 
        "price": float(price), 
        "link": paypal_link, # This is the BUY BUTTON link
        "image_url": img_url,
        "status": "active",
        "timestamp": int(time.time())
    }
    
    db.insert(0, new_prod)
    with open(DB_FILE, "w") as f: json.dump(db, f, indent=2)

    # Inject into DryPaper Store
    try:
        headers = {
            "apikey": SUPABASE_KEY, 
            "Authorization": f"Bearer {SUPABASE_KEY}", 
            "Content-Type": "application/json",
            "Prefer": "return=minimal"
        }
        r = requests.post(f"{SUPABASE_URL}/rest/v1/drypaper_assets", headers=headers, data=json.dumps(new_prod))
        if r.status_code == 201: print("✅ LIVE ON STORE!")
    except Exception as e: print(f"⚠️ Store Sync Failed: {e}")

print("✅ Operations Complete.")
# Inject into DryPaper Store (WITH ERROR LOG)
try:
    headers = {
        "apikey": SUPABASE_KEY, 
        "Authorization": f"Bearer {SUPABASE_KEY}", 
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }
    r = requests.post(f"{SUPABASE_URL}/rest/v1/drypaper_assets", headers=headers, json=new_prod)
    if r.status_code == 201: 
        print("✅ LIVE ON STORE!")
    else:
        print(f"❌ Supabase Error {r.status_code}: {r.text}")
except Exception as e: 
    print(f"⚠️ Store Sync Failed: {e}")


