import json, os, smtplib, requests, random, re, time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

print("--- 🏴‍☠️ MARKETING: HUNTER PRO MAX (MULTI-ENGINE) ---")

# SECRETS
DEVTO_KEY = os.environ.get("DEVTO_API_KEY")
SMTP_EMAIL = os.environ.get("SMTP_EMAIL")
SMTP_PASS = os.environ.get("SMTP_PASSWORD")
DB_FILE = "products.json"

if not os.path.exists(DB_FILE):
    print("⚠️ No ammo. Exiting.")
    exit()

with open(DB_FILE, "r") as f: db = json.load(f)
latest = db[0]

# --- 1. MULTI-ENGINE LEAD HUNTER ---
def clean_emails(text):
    # Regex to extract emails
    found = set(re.findall(r"[a-zA-Z0-9._%+-]+@gmail\.com", text))
    # Filter junk
    return [e for e in found if "example" not in e and "domain" not in e and len(e)>8]

def hunt_leads():
    print("🕵️ Hunting leads across multiple engines...")
    leads = []
    
    # Target Niches (Mix it up)
    niches = ["marketing agency owner", "seo consultant", "web design agency founder", "digital marketing ceo"]
    target = random.choice(niches)
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    # ENGINE 1: DuckDuckGo Lite
    try:
        print(f"🔎 Engine 1 (DDG): Scanning for '{target}'...")
        url = f"https://lite.duckduckgo.com/lite/?q={target}+%22gmail.com%22"
        r = requests.get(url, headers=headers, timeout=10)
        found = clean_emails(r.text)
        leads += found
        print(f"   ✅ DDG Found: {len(found)}")
    except: print("   ❌ DDG Blocked")

    # ENGINE 2: Yahoo Search (Backup)
    try:
        if len(leads) < 5: # Sirf tab chalao agar DDG ne kam diya
            print(f"🔎 Engine 2 (Yahoo): Scanning for '{target}'...")
            url = f"https://search.yahoo.com/search?p={target}+%22gmail.com%22"
            r = requests.get(url, headers=headers, timeout=10)
            found = clean_emails(r.text)
            leads += found
            print(f"   ✅ Yahoo Found: {len(found)}")
    except: print("   ❌ Yahoo Blocked")
    
    # ENGINE 3: Ask.com (Last Resort)
    try:
        if len(leads) < 5:
            print(f"🔎 Engine 3 (Ask): Scanning for '{target}'...")
            url = f"https://www.ask.com/web?q={target}+%22gmail.com%22"
            r = requests.get(url, headers=headers, timeout=10)
            found = clean_emails(r.text)
            leads += found
            print(f"   ✅ Ask Found: {len(found)}")
    except: print("   ❌ Ask Blocked")

    unique_leads = list(set(leads))[:15] # Limit 15 to stay safe
    print(f"💀 Total Unique Leads: {len(unique_leads)}")
    return unique_leads

# --- 2. SENDER ---
def send_cold_email(to_email, product_name, product_link, price):
    if not SMTP_EMAIL or not SMTP_PASS: return

    scripts = [
        {"s": "Collaboration?", "b": f"Hi,\n\nI built {product_name} for agencies.\n\nCheck it: {product_link}\n\nThanks,\nRajat"},
        {"s": "Tool for your agency", "b": f"Hey,\n\nFound you online. {product_name} helps you scale.\n\nIt's ${price} here: {product_link}\n\nCheers,\nRajat"}
    ]
    script = random.choice(scripts)
    
    msg = MIMEMultipart()
    msg['From'] = f"Rajat <{SMTP_EMAIL}>"
    msg['To'] = to_email
    msg['Subject'] = script["s"]
    msg.attach(MIMEText(script["b"], 'plain'))
    
    try:
        server = smtplib.SMTP_SSL('smtp.hostinger.com', 465)
        server.login(SMTP_EMAIL, SMTP_PASS)
        server.sendmail(SMTP_EMAIL, to_email, msg.as_string())
        server.quit()
        print(f"🚀 SENT TO: {to_email}")
        time.sleep(random.randint(3, 7)) # Human Delay
    except Exception as e: print(f"❌ Send Error: {e}")

# --- 3. EXECUTE ---

# A. RSS & Dev.to
def update_rss():
    rss = '<?xml version="1.0" encoding="UTF-8" ?><rss version="2.0"><channel><title>DryPaper HQ</title><link>https://www.drypaperhq.com</link>'
    for item in db[:10]:
        rss += f'<item><title>{item["name"]}</title><link>https://www.drypaperhq.com/{item["file"]}</link><description>{item["desc"]}</description></item>'
    rss += '</channel></rss>'
    with open("feed.xml", "w") as f: f.write(rss)
update_rss()

if DEVTO_KEY:
    try: requests.post("https://dev.to/api/articles", headers={"api-key": DEVTO_KEY, "Content-Type": "application/json"}, json={"article": {"title": f"New Tool: {latest['name']}", "body_markdown": f"# {latest['name']}\n\nLink: https://www.drypaperhq.com/{latest['file']}", "published": True, "tags": ["agency"]}})
    except: pass

# B. ATTACK
fresh_leads = hunt_leads()
if fresh_leads:
    print(f"⚔️ ATTACKING {len(fresh_leads)} TARGETS...")
    for lead in fresh_leads:
        send_cold_email(lead, latest['name'], f"https://www.drypaperhq.com/{latest['file']}", latest['price'])
else:
    print("⚠️ All engines blocked. Will retry tomorrow.")

print("✅ DAY COMPLETE.")

