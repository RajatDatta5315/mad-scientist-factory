import json, os, smtplib, requests, random, re, time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

print("--- 🏴‍☠️ MARKETING: SOCIAL SNIPER EDITION ---")

# SECRETS
DEVTO_KEY = os.environ.get("DEVTO_API_KEY")
SMTP_EMAIL = os.environ.get("SMTP_EMAIL")
SMTP_PASS = os.environ.get("SMTP_PASSWORD")
TARGET_EMAIL = os.environ.get("TARGET_EMAIL")
DB_FILE = "products.json"

if not os.path.exists(DB_FILE):
    print("⚠️ No ammo. Exiting.")
    exit()

with open(DB_FILE, "r") as f: db = json.load(f)
latest = db[0]

# --- 1. THE SOCIAL SNIPER (Targeting Insta/FB Bios) ---
def clean_emails(text):
    # Regex to find emails
    found = set(re.findall(r"[a-zA-Z0-9._%+-]+@gmail\.com", text))
    # Filter junk
    return [e for e in found if "example" not in e and "domain" not in e and len(e)>8]

def hunt_leads():
    print("🕵️ Sniping leads from Social Media Bios...")
    leads = []
    
    # Target Keywords (Ye change hote rahenge)
    niches = ["marketing agency", "digital agency", "seo expert", "web designer", "content creator"]
    niche = random.choice(niches)
    
    # Fake Headers (Browser Rotation)
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"
    ]
    headers = {"User-Agent": random.choice(user_agents)}

    # STRATEGY 1: Instagram via Bing (Less Blocked)
    # Search Query: site:instagram.com "marketing agency" "@gmail.com"
    try:
        print(f"🎯 Target: Instagram Bios for '{niche}'...")
        query = f"site:instagram.com \"{niche}\" \"@gmail.com\""
        url = f"https://www.bing.com/search?q={query}&count=30"
        
        r = requests.get(url, headers=headers, timeout=10)
        found = clean_emails(r.text)
        leads += found
        print(f"   ✅ Insta Leads: {len(found)}")
    except: print("   ❌ Insta Blocked")

    # STRATEGY 2: Facebook via Yahoo (Backup)
    try:
        if len(leads) < 5:
            print(f"🎯 Target: Facebook About Pages for '{niche}'...")
            query = f"site:facebook.com \"{niche}\" \"@gmail.com\""
            url = f"https://search.yahoo.com/search?p={query}"
            
            r = requests.get(url, headers=headers, timeout=10)
            found = clean_emails(r.text)
            leads += found
            print(f"   ✅ FB Leads: {len(found)}")
    except: print("   ❌ FB Blocked")

    unique_leads = list(set(leads))[:20] # Limit to 20
    print(f"💀 Total Sniped Leads: {len(unique_leads)}")
    return unique_leads

# --- 2. COLD EMAIL SENDER ---
def send_cold_email(to_email, product_name, product_link, price):
    if not SMTP_EMAIL or not SMTP_PASS: return

    scripts = [
        {"s": "Quick collab?", "b": f"Hi,\n\nI saw your agency on Instagram/FB.\n\nI built {product_name} specifically for digital agencies. It automates the boring stuff.\n\nCheck it out here: {product_link}\n\nBest,\nRajat"},
        {"s": "Tool for your team", "b": f"Hey,\n\nFound your contact in your bio. \n\nWe just launched {product_name} to help agencies scale.\n\nUsually ${price}, grab it here: {product_link}\n\nCheers,\nRajat"}
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
        time.sleep(random.randint(2, 5)) 
    except: pass

# --- 3. EXECUTE ---

# A. RSS Update
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
else:
    print("⚠️ No leads found today. Try manually adding leads.txt later.")

# C. REPORT TO BOSS
if os.environ.get("EMAIL_USER"):
    try:
        msg = MIMEMultipart()
        msg['From'] = os.environ.get("EMAIL_USER")
        msg['To'] = TARGET_EMAIL
        msg['Subject'] = f"✅ WAR REPORT: {len(fresh_leads)} EMAILS SENT"
        
        # List of people we emailed (First 5 only to keep email short)
        sent_list = "\n".join(fresh_leads[:5])
        
        body = f"""
        Boss, 
        
        Product: {latest['name']} is LIVE.
        
        🔫 Total Targets Hit: {len(fresh_leads)}
        
        Sample Targets:
        {sent_list}
        ... and more.
        
        Waiting for your Masterplan.
        """
        msg.attach(MIMEText(body, 'plain'))
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        s.login(os.environ.get("EMAIL_USER"), os.environ.get("EMAIL_PASS"))
        s.sendmail(os.environ.get("EMAIL_USER"), TARGET_EMAIL, msg.as_string())
        s.quit()
        print("✅ Report Sent")
    except Exception as e: print(f"❌ Report Failed: {e}")

print("✅ DAY COMPLETE.")

