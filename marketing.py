import json, os, smtplib, requests, random, re, time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

print("--- 🏴‍☠️ MARKETING: HUNTER PRO MAX (WITH REPORTING) ---")

# SECRETS
DEVTO_KEY = os.environ.get("DEVTO_API_KEY")
SMTP_EMAIL = os.environ.get("SMTP_EMAIL")
SMTP_PASS = os.environ.get("SMTP_PASSWORD")
TARGET_EMAIL = os.environ.get("TARGET_EMAIL") # Reporting ke liye
DB_FILE = "products.json"

if not os.path.exists(DB_FILE):
    print("⚠️ No ammo. Exiting.")
    exit()

with open(DB_FILE, "r") as f: db = json.load(f)
latest = db[0]

# --- 1. MULTI-ENGINE LEAD HUNTER ---
def clean_emails(text):
    found = set(re.findall(r"[a-zA-Z0-9._%+-]+@gmail\.com", text))
    return [e for e in found if "example" not in e and "domain" not in e and len(e)>8]

def hunt_leads():
    print("🕵️ Hunting leads...")
    leads = []
    niches = ["marketing agency owner", "seo consultant", "web design agency", "digital marketing ceo"]
    target = random.choice(niches)
    
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}

    # ENGINE 1: DuckDuckGo Lite
    try:
        print(f"🔎 DDG Lite: '{target}'...")
        r = requests.get(f"https://lite.duckduckgo.com/lite/?q={target}+%22gmail.com%22", headers=headers, timeout=10)
        leads += clean_emails(r.text)
    except: pass

    # ENGINE 2: Yahoo (Backup)
    try:
        if len(leads) < 5:
            print(f"🔎 Yahoo: '{target}'...")
            r = requests.get(f"https://search.yahoo.com/search?p={target}+%22gmail.com%22", headers=headers, timeout=10)
            leads += clean_emails(r.text)
    except: pass

    # ENGINE 3: Ask.com (Last Resort)
    try:
        if len(leads) < 5:
            print(f"🔎 Ask.com: '{target}'...")
            r = requests.get(f"https://www.ask.com/web?q={target}+%22gmail.com%22", headers=headers, timeout=10)
            leads += clean_emails(r.text)
    except: pass

    return list(set(leads))[:15]

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
        time.sleep(random.randint(3, 7))
    except: pass

# --- 3. EXECUTE ---
# A. RSS
def update_rss():
    rss = '<?xml version="1.0" encoding="UTF-8" ?><rss version="2.0"><channel><title>DryPaper HQ</title><link>https://www.drypaperhq.com</link>'
    for item in db[:10]:
        rss += f'<item><title>{item["name"]}</title><link>https://www.drypaperhq.com/{item["file"]}</link><description>{item["desc"]}</description></item>'
    rss += '</channel></rss>'
    with open("feed.xml", "w") as f: f.write(rss)
update_rss()

# B. ATTACK
fresh_leads = hunt_leads()
if fresh_leads:
    print(f"⚔️ ATTACKING {len(fresh_leads)} TARGETS...")
    for lead in fresh_leads:
        send_cold_email(lead, latest['name'], f"https://www.drypaperhq.com/{latest['file']}", latest['price'])

# C. BOSS REPORT (Ye Missing Tha!)
if os.environ.get("EMAIL_USER"):
    try:
        msg = MIMEMultipart()
        msg['From'] = os.environ.get("EMAIL_USER")
        msg['To'] = TARGET_EMAIL
        msg['Subject'] = f"✅ MISSION SUCCESS: {latest['name']}"
        body = f"Boss,\n\nProduct Live: {latest['name']}\nLeads Hunted & Emailed: {len(fresh_leads)}\n\nStore is Active. Money mode on."
        msg.attach(MIMEText(body, 'plain'))
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        s.login(os.environ.get("EMAIL_USER"), os.environ.get("EMAIL_PASS"))
        s.sendmail(os.environ.get("EMAIL_USER"), TARGET_EMAIL, msg.as_string())
        s.quit()
        print("✅ Report Sent to Boss")
    except Exception as e: print(f"❌ Report Failed: {e}")

print("✅ DAY COMPLETE.")

