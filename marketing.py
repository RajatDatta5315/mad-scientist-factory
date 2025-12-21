import json, os, smtplib, requests, random, re, time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

print("--- 🏴‍☠️ MARKETING: WARLORD EDITION (FULL AUTO) ---")

# SECRETS
DEVTO_KEY = os.environ.get("DEVTO_API_KEY")
SMTP_EMAIL = os.environ.get("SMTP_EMAIL") # Hostinger Email
SMTP_PASS = os.environ.get("SMTP_PASSWORD")
DB_FILE = "products.json"

if not os.path.exists(DB_FILE):
    print("⚠️ No ammo. Exiting.")
    exit()

with open(DB_FILE, "r") as f: db = json.load(f)
latest = db[0]

# --- 1. DUAL-ENGINE HUNTER (KHUD EMAILS DHUNDEGA) ---
def hunt_leads():
    print("🕵️ Hunting fresh souls (Leads)...")
    leads = []
    
    # Target Keywords
    niches = ["marketing agency", "seo firm", "web design company", "consulting business"]
    target = random.choice(niches)
    
    # Fake Browser Headers
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    # SEARCH ENGINE 1: DuckDuckGo (HTML)
    try:
        print(f"🔎 Scanning DuckDuckGo for '{target}'...")
        url = f"https://html.duckduckgo.com/html/?q={target} owner %22gmail.com%22"
        r = requests.get(url, headers=headers, timeout=10)
        # HTML se emails nikalna
        found = set(re.findall(r"[a-zA-Z0-9._%+-]+@gmail\.com", r.text))
        leads += [e for e in found if "example" not in e and len(e)>8]
    except: pass

    # SEARCH ENGINE 2: Bing (Backup)
    try:
        url_bing = f"https://www.bing.com/search?q={target}+owner+%22gmail.com%22"
        r = requests.get(url_bing, headers=headers, timeout=10)
        found = set(re.findall(r"[a-zA-Z0-9._%+-]+@gmail\.com", r.text))
        leads += [e for e in found if "example" not in e and len(e)>8]
    except: pass
    
    unique_leads = list(set(leads))[:15] # Safe Limit
    print(f"💀 Total Fresh Leads Found: {len(unique_leads)}")
    return unique_leads

# --- 2. COLD EMAIL SENDER (HOSTINGER SE BHEJEGA) ---
def send_cold_email(to_email, product_name, product_link, price):
    if not SMTP_EMAIL or not SMTP_PASS: return

    scripts = [
        {"s": "Collaboration?", "b": f"Hi,\n\nI run DryPaper HQ. We built {product_name} to automate agency work.\n\nCheck it: {product_link}\n\nThanks,\nRajat"},
        {"s": "Question about your process", "b": f"Hey,\n\nFound your agency online. I built a tool ({product_name}) that saves time.\n\nIt's ${price} here: {product_link}\n\nCheers,\nRajat"}
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
        print(f"🚀 SENT AUTO-MAIL TO: {to_email}")
        time.sleep(5) 
    except: pass

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

# B. AUTO-ATTACK (No Boss Report, Just Action)
fresh_leads = hunt_leads()
if fresh_leads:
    print(f"⚔️ ATTACKING {len(fresh_leads)} TARGETS...")
    for lead in fresh_leads:
        send_cold_email(lead, latest['name'], f"https://www.drypaperhq.com/{latest['file']}", latest['price'])

# C. FINAL CONFIRMATION EMAIL TO YOU
if os.environ.get("EMAIL_USER"):
    try:
        msg = MIMEMultipart()
        msg['From'] = os.environ.get("EMAIL_USER")
        msg['To'] = os.environ.get("TARGET_EMAIL")
        msg['Subject'] = f"✅ MISSION SUCCESS: {latest['name']}"
        body = f"Boss,\n\nProduct Live: {latest['name']}\n\n💀 Leads Hunted: {len(fresh_leads)}\n🚀 Cold Emails Sent: {len(fresh_leads)}\n\nEverything is automated. Sleep tight."
        msg.attach(MIMEText(body, 'plain'))
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        s.login(os.environ.get("EMAIL_USER"), os.environ.get("EMAIL_PASS"))
        s.sendmail(os.environ.get("EMAIL_USER"), os.environ.get("TARGET_EMAIL"), msg.as_string())
        s.quit()
    except: pass

print("✅ DAY COMPLETE.")

