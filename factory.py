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
    
    # 7. SAVE TO DB & STORE (RE-CONFIGURED)
    # Price ko string se float/int me convert karna zaroori hai
    new_prod = {
        "name": name, 
        "description": desc.replace('"', ''), 
        "price": int(price), 
        "link": paypal_link, # <--- YE PAYPAL LINK HI JAYEGA
        "image_url": img_url,
        "status": "active"
    }
    
    # 8. INJECT INTO SUPABASE WITH ERROR TRACKING
    try:
        headers = {
            "apikey": SUPABASE_KEY, 
            "Authorization": f"Bearer {SUPABASE_KEY}", 
            "Content-Type": "application/json",
            "Prefer": "return=representation" # Representations se data wapas milta hai
        }
        r = requests.post(f"{SUPABASE_URL}/rest/v1/drypaper_assets", headers=headers, json=new_prod)
        
        if r.status_code == 201:
            print(f"✅ SUCCESS: {name} is live on DryPaper (Price: ${price})")
        else:
            print(f"❌ SUPABASE FAIL: {r.status_code}")
            print(f"Response: {r.text}")
            
    except Exception as e:
        print(f"⚠️ STORE SYNC CRASHED: {e}")

print("✅ Operations Complete.")
