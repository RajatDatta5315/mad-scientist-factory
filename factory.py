import requests, json, re, sys, os, random, time, urllib.parse
from PIL import Image, ImageDraw, ImageFont # Image generation ke liye

print("--- 🏭 FACTORY: SIGNATURE EDITION ---")

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

def create_signature_image(text):
    """Creates a Minimal Black & White Signature Cover"""
    try:
        width, height = 800, 600
        img = Image.new('RGB', (width, height), color='black')
        draw = ImageDraw.Draw(img)
        
        # Centering Text (Approximation)
        # Linux server pe fancy fonts nahi hote, hum default clean use karenge
        # Text ko thoda center mein laane ka logic
        text_x = 100
        text_y = 280
        
        draw.text((text_x, text_y), text.upper(), fill='white')
        draw.rectangle([text_x, text_y + 20, text_x + 100, text_y + 22], fill='white') # Underline vibe
        
        filename = f"cover_{int(time.time())}.jpg"
        img.save(filename)
        return filename
    except Exception as e:
        print(f"Image Gen Error: {e}")
        return None

def upload_to_supabase(filename, bucket):
    try:
        with open(filename, 'rb') as f: file_data = f.read()
        url = f"{SUPABASE_URL}/storage/v1/object/{bucket}/{filename}"
        headers = {"Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "text/html" if filename.endswith(".html") else "image/jpeg"}
        r = requests.post(url, headers=headers, data=file_data)
        if r.status_code == 200:
            return f"{SUPABASE_URL}/storage/v1/object/public/{bucket}/{filename}"
    except Exception as e: print(f"Upload Error: {e}")
    return None

# --- MAIN EXECUTION ---
print("🚀 Starting Production Cycle...")

# 1. IDEA
name = ask_ai("Output ONLY the name. Minimal, Abstract, One Word if possible.", "Suggest a dark web style AI tool name.")
name = re.sub(r'[^a-zA-Z0-9 ]', '', name).strip()
if not name: name = f"Protocol_{int(time.time())}"

# 2. CODE
safe_name = f"tool_{int(time.time())}.html"
tool_code = ask_ai("Output HTML only. Dark Theme. Minimal.", f"Code for {name}.")
tool_code = tool_code.replace("```html", "").replace("```", "")
with open(safe_name, "w") as f: f.write(tool_code)

# 3. UPLOAD FILES
file_url = upload_to_supabase(safe_name, "product-files")

# 4. GENERATE SIGNATURE IMAGE
cover_file = create_signature_image(name)
if cover_file:
    img_url = upload_to_supabase(cover_file, "product-images")
else:
    img_url = "https://placehold.co/600x400/000000/ffffff?text=" + name

# 5. MARKETING & PRICE
desc = ask_ai("One sentence. Mysterious.", f"Describe {name} functionality.")
price = random.choice(["29", "49"])

# 6. PAYPAL LINK
paypal_link = f"https://www.paypal.com/cgi-bin/webscr?cmd=_xclick&business={PAYPAL_EMAIL}&item_name={urllib.parse.quote(name)}&amount={price}&currency_code=USD&return={urllib.parse.quote(file_url)}"

# 7. SAVE TO DB
new_prod = {
    "name": name, 
    "description": desc.replace('"', ''), 
    "price": int(price), 
    "link": paypal_link,
    "image_url": img_url,
    "status": "active"
}

headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json", "Prefer": "return=minimal"}
requests.post(f"{SUPABASE_URL}/rest/v1/drypaper_assets", headers=headers, json=new_prod)

print(f"✅ DONE. {name} is LIVE.")
