import requests, json, re, sys, os, random, time, urllib.parse
from PIL import Image, ImageDraw, ImageFont

print("--- 🏭 FACTORY: SIGNATURE EDITION V2 ---")

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
PAYPAL_EMAIL = os.environ.get("PAYPAL_EMAIL")
SUPABASE_URL = os.environ.get("NEXT_PUBLIC_SUPABASE_URL") 
SUPABASE_KEY = os.environ.get("NEXT_PUBLIC_SUPABASE_ANON_KEY")

if not GROQ_API_KEY or not PAYPAL_EMAIL or not SUPABASE_URL:
    print("❌ Critical Secrets Missing.")
    sys.exit(1)

def ask_ai(system_prompt, user_prompt):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": "llama-3.3-70b-versatile", "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]}
    try:
        r = requests.post(url, headers=headers, json=payload)
        if r.status_code == 200: return r.json()['choices'][0]['message']['content'].strip()
    except Exception as e: print(f"AI Error: {e}")
    return ""

def create_signature_image(text):
    try:
        width, height = 800, 600
        img = Image.new('RGB', (width, height), color='black')
        draw = ImageDraw.Draw(img)
        draw.text((100, 280), f"> {text.upper()}_", fill='white')
        draw.line([100, 310, 300, 310], fill='white', width=2)
        filename = f"cover_{int(time.time())}.jpg"
        img.save(filename)
        return filename
    except Exception as e:
        print(f"Image Error: {e}")
        return None

def upload_to_supabase(filename, bucket):
    try:
        with open(filename, 'rb') as f: file_data = f.read()
        url = f"{SUPABASE_URL}/storage/v1/object/{bucket}/{filename}"
        headers = {"Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "text/html" if filename.endswith(".html") else "image/jpeg"}
        r = requests.post(url, headers=headers, data=file_data)
        return f"{SUPABASE_URL}/storage/v1/object/public/{bucket}/{filename}"
    except: return None

print("🚀 Starting Production Cycle...")
name = ask_ai("Output ONLY a 1-word tech name.", "Suggest a dark/minimal AI tool name.")
name = re.sub(r'[^a-zA-Z0-9]', '', name).strip() or f"OX_{int(time.time())}"

safe_name = f"tool_{int(time.time())}.html"
tool_code = ask_ai("Output HTML code only.", f"Single-page dark app for {name}.")
tool_code = tool_code.replace("```html", "").replace("```", "")
with open(safe_name, "w") as f: f.write(tool_code)

file_url = upload_to_supabase(safe_name, "product-files")
cover_file = create_signature_image(name)
img_url = upload_to_supabase(cover_file, "product-images") if cover_file else ""

desc = ask_ai("Write 1 mysterious sentence.", f"What does {name} do?")
price = random.choice([29, 49, 99])
paypal_link = f"https://www.paypal.com/cgi-bin/webscr?cmd=_xclick&business={PAYPAL_EMAIL}&item_name={name}&amount={price}&currency_code=USD&return={file_url}"

new_prod = {"name": name, "description": desc, "price": price, "link": paypal_link, "image_url": img_url, "status": "active"}
headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}
r = requests.post(f"{SUPABASE_URL}/rest/v1/drypaper_assets", headers=headers, json=new_prod)

print(f"✅ DEPLOYED: {name}")
