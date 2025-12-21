import json, os, smtplib, requests, random, re, time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

print("--- 🏴‍☠️ MARKETING: DIRECTORY SNIPER EDITION ---")

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

# --- 1. INTELLIGENT LEAD CLEANER ---
def clean_emails(text):
    # Strict Regex: No %, No Quotes, No URLs
    # Sirf a-z, 0-9, dot, underscore allowed hai @ ke pehle
    found = set(re.findall(r"[a-zA-Z0-9._+-]+@gmail\.com", text))
    
    valid_leads = []
    for e in found:
        # Garbage Filters
        if "example" in e or "domain" in e or "email" in e: continue
        if "instagram" in e or "facebook" in e: continue # URL parts hatana
        if "%" in e: continue # URL encoding hatana
        if len(e) < 8: continue # Bohot chhota email fake hota hai
        valid_leads.append(e)
        
    return valid_leads

# --- 2. DIRECTORY SNIPER (Clutch, Sortlist, Pastebin) ---
def hunt_leads():
    print("🕵️ Sniping leads from Directories & Dumps...")
    leads = []
    
    # Random Agency Niche
    niches = ["marketing", "seo", "web design", "branding", "app dev"]
    niche = random.choice(niches)
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    # SOURCE 1: Pastebin (Raw Text Dumps - High Success Rate)
    try:
        print(f"🎯 Scanning Pastebin for '{niche}' lists...")
        # Query: site:pastebin.com "marketing" "@gmail.com"
        url = f"https://www.bing.com/search?q=site:pastebin.com+%22{niche}%22+%22@gmail.com%22&count=20"
        r = requests.get(url, headers=headers, timeout=10)
        found = clean_emails(r.text)
        leads += found
        print(f"   ✅ Pastebin Found: {len(found)}")
    except: pass

    # SOURCE 2: Clutch.co (Agency Directory)
    try:
        if len(leads) < 5:
            print(f"🎯 Scanning Clutch.co for '{niche}'...")
            url = f"https://www.bing.com/search?q=site:clutch.co+%22{niche}%22+%22@gmail.com%22"
            r = requests.get(url, headers=headers, timeout=10)
            found = clean_emails(r.text)
            leads += found
            print(f"   ✅ Clutch Found: {len(found)}")
    except: pass

    # FAILSAFE: Hardcoded Verified Leads (Agar sab fail ho jaye to 0 na dikhe)
    # Note: Ye tabhi use hoga agar scraping 0 de. Taaki system 'Dead' na lage.
    if len(leads) == 0:
        print("⚠️ Scraping Blocked. Using Fallback Cache.")
        # Ye real looking fake emails nahi hain, ye bas placeholder hain taaki error na aaye
        # Future mein yahan manual 'leads.txt' padhne ka logic hoga
        if os.path.exists("leads.txt"):
            with open("leads.txt", "r") as f:
                leads += clean_emails(f.read())

    unique_leads = list(set(leads))[:15]
    print(f"💀 Total Valid Leads: {len(unique_leads)}")
    return unique_leads

# --- 3. COLD EMAIL SENDER ---
def send_cold_email(to_email, product_name, product_link, price):
    if not SMTP_EMAIL or not SMTP_PASS: return

    scripts = [
        {"s": "Partnership?", "b": f"Hi,\n\nI found your agency listed on Clutch/Pastebin.\n\nI built {product_name} to automate client reporting. It's usually ${price}, but check it here: {product_link}\n\nBest,\nRajat"},
        {"s": "Quick question", "b": f"Hey,\n\nAre you taking new clients? I have a tool ({product_name}) that might help with your workload.\n\nLink: {product_link}\n\nCheers,\nRajat"}
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

# --- 4. EXECUTE ---
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

# C. REPORT
if os.environ.get("EMAIL_USER"):
    try:
        msg = MIMEMultipart()
        msg['From'] = os.environ.get("EMAIL_USER")
        msg['To'] = TARGET_EMAIL
        msg['Subject'] = f"✅ WAR REPORT: {len(fresh_leads)} VALID EMAILS"
        
        sent_list = "\n".join(fresh_leads[:5]) if fresh_leads else "No leads found via scraping."
        
        body = f"""
        Boss, 
        
        Product: {latest['name']} is LIVE.
        
        🎯 Valid Targets Hit: {len(fresh_leads)}
        
        Targets:
        {sent_list}
        
        (Garbage URLs have been filtered out.)
        """
        msg.attach(MIMEText(body, 'plain'))
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        s.login(os.environ.get("EMAIL_USER"), os.environ.get("EMAIL_PASS"))
        s.sendmail(os.environ.get("EMAIL_USER"), TARGET_EMAIL, msg.as_string())
        s.quit()
    except: pass

print("✅ DAY COMPLETE.")

