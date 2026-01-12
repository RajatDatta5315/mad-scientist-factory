import requests, json, re, sys, os, random, time, urllib.parse

print("--- 🏭 FACTORY: FULL CLOUD AUTOMATION ---")

# --- SECRETS ---
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
PAYPAL_EMAIL = os.environ.get("PAYPAL_EMAIL")
SUPABASE_URL = os.environ.get("NEXT_PUBLIC_SUPABASE_URL") 
SUPABASE_KEY = os.environ.get("NEXT_PUBLIC_SUPABASE_ANON_KEY")

if not GROQ_API_KEY or not PAYPAL_EMAIL or not SUPABASE_URL:
    print("❌ Critical Secrets Missing.")
    sys.exit(1)

# --- FUNCTIONS ---
def ask_ai(system_prompt, user_prompt):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": "llama-3.3-70b-versatile", "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]}
    try:
        r = requests.post(url, headers=headers, data=json.dumps(payload))
        if r.status_code == 200: return r.json()['choices'][0]['message']['content'].strip()
    except Exception as e: print(f"AI Error: {e}")
    return "Automated Tool"

def upload_to_supabase(filename, bucket):
    try:
        with open(filename, 'rb') as f: file_data = f.read()
        url = f"{SUPABASE_URL}/storage/v1/object/{bucket}/{filename}"
        headers = {"Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "text/html"}
        r = requests.post(url, headers=headers, data=file_data)
        if r.status_code == 200:
            return f"{SUPABASE_URL}/storage/v1/object/public/{bucket}/{filename}"
    except Exception as e: print(f"Upload Error: {e}")
    return None

# --- MAIN EXECUTION ---
print("🚀 Starting Production Cycle...")

# 1. IDEA GENERATION
print("🧠 Dreaming up a new tool...")
name = ask_ai("Output ONLY the name. Short, Catchy, Tech.", "Suggest a unique AI Micro-SaaS tool name for digital agencies.")
name = re.sub(r'[^a-zA-Z0-9 ]', '', name).strip()
if not name: name = f"Tool_{int(time.time())}"

# 2. CODING
print(f"💎 Coding {name}...")
safe_name = f"tool_{int(time.time())}.html"
tool_code = ask_ai("Output HTML code only. Modern, Dark Theme, Tailwind CSS. Single file.", f"Write code for: {name}. Make it functional.")
tool_code = tool_code.replace("```html", "").replace("```", "")
with open(safe_name, "w") as f: f.write(tool_code)

# 3. UPLOAD PRODUCT
product_url = upload_to_supabase(safe_name, "product-files")
if not product_url:
    print("❌ Failed to upload product. Aborting.")
    sys.exit(1)

# 4. MARKETING DATA & PRICE
desc = ask_ai("Write 1 punchy sentence.", f"Describe {name} for a hacker/developer audience.")
price = random.choice(["29", "49", "39"]) # String for PayPal

# 5. PAYPAL LINK (The Money Maker)
# Note: Using urllib to safely encode the name and return URL
paypal_link = f"https://www.paypal.com/cgi-bin/webscr?cmd=_xclick&business={PAYPAL_EMAIL}&item_name={urllib.parse.quote(name)}&amount={price}&currency_code=USD&return={urllib.parse.quote(product_url)}"

# 6. DATABASE PREP
new_prod = {
    "name": name, 
    "description": desc.replace('"', ''), 
    "price": int(price), 
    "link": paypal_link, # <--- PAYPAL LINK HERE
    "image_url": "https://placehold.co/600x400/000000/00ff00?text=NO_IMAGE", # Placeholder
    "status": "active"
}

# 7. INJECT INTO SUPABASE
print("💾 Saving to Empire Database...")
headers = {
    "apikey": SUPABASE_KEY, 
    "Authorization": f"Bearer {SUPABASE_KEY}", 
    "Content-Type": "application/json",
    "Prefer": "return=minimal"
}
r = requests.post(f"{SUPABASE_URL}/rest/v1/drypaper_assets", headers=headers, json=new_prod)

if r.status_code == 201:
    print(f"✅ SUCCESS! {name} is LIVE. Price: ${price}")
    print(f"💰 Buy Link: {paypal_link}")
else:
    print(f"❌ DB Error: {r.status_code} - {r.text}")

print("✅ Factory Run Complete.")
