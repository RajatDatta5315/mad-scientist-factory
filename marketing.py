import json, os, smtplib, requests, random, re, time, urllib.parse
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

print("--- 🏴‍☠️ MARKETING: TEXT FILE HUNTER ---")

# SECRETS
SMTP_EMAIL = os.environ.get("SMTP_EMAIL")
SMTP_PASS = os.environ.get("SMTP_PASSWORD")
TARGET_EMAIL = os.environ.get("TARGET_EMAIL")
DB_FILE = "products.json"

if not os.path.exists(DB_FILE):
    print("⚠️ No ammo. Exiting.")
    exit()

with open(DB_FILE, "r") as f: db = json.load(f)
latest = db[0]

# --- 1. ADVANCED CLEANER (NO MORE JUNK) ---
def clean_emails(raw_text):
    # Step 1: Decode URL (Convert %22 to ")
    decoded_text = urllib.parse.unquote(raw_text)
    
    # Step 2: Find Emails
    found = set(re.findall(r"[a-zA-Z0-9._+-]+@gmail\.com", decoded_text))
    
    valid_leads = []
    for e in found:
        # Filter 1: Length (Too short = fake)
        if len(e) < 10: continue
        # Filter 2: Starts with number (Likely junk code)
        if e[0].isdigit(): continue
        # Filter 3: Keywords
        if "example" in e or "domain" in e or "email" in e: continue
        
        valid_leads.append(e)
        
    return valid_leads

# --- 2. TEXT FILE HUNTER ---
def hunt_leads():
    print("🕵️ Hunting for exposed Lead Lists (filetype:txt)...")
    leads = []
    
    # Target: Files containing lists of emails
    niches = ["marketing", "agency", "ceo", "leads"]
    niche = random.choice(niches)
    
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}

    # STRATEGY: Search for uploaded text files with gmail lists
    # Query: "marketing" "gmail.com" filetype:txt
    try:
        print(f"🎯 Scanning public text files for '{niche}'...")
        url = f"https://www.bing.com/search?q=%22{niche}%22+%22gmail.com%22+filetype:txt&count=10"
        r = requests.get(url, headers=headers, timeout=10)
        
        # Extract URLs of text files from search results
        links = re.findall(r'href="(https?://[^"]+\.txt)"', r.text)
        
        # Scan inside those text files
        for link in links[:3]: # Check top 3 files
            try:
                print(f"   📄 Reading file: {link[:30]}...")
                file_req = requests.get(link, headers=headers, timeout=5)
                found = clean_emails(file_req.text)
                leads += found
                if len(leads) > 20: break # Bas 20 mil gayi to ruk jao
            except: pass
            
    except: pass

    # FAILSAFE: Using Pastebin Search as backup
    if len(leads) == 0:
        try:
            print("   ⚠️ Switch to Pastebin Search...")
            url = f"https://www.bing.com/search?q=site:pastebin.com+%22{niche}%22+%22gmail.com%22"
            r = requests.get(url, headers=headers, timeout=10)
            leads += clean_emails(r.text)
        except: pass

    unique_leads = list(set(leads))[:15]
    print(f"💀 Total Valid Leads: {len(unique_leads)}")
    return unique_leads

# --- 3. SENDER ---
def send_cold_email(to_email, product_name, product_link, price):
    if not SMTP_EMAIL or not SMTP_PASS: return

    scripts = [
        {"s": "Partnership?", "b": f"Hi,\n\nI built {product_name} to automate agency work.\n\nCheck it: {product_link}\n\nBest,\nRajat"},
        {"s": "Tool for your team", "b": f"Hey,\n\nAre you taking new clients? {product_name} might help you scale.\n\nLink: {product_link}\n\nCheers,\nRajat"}
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
# RSS Update
def update_rss():
    rss = '<?xml version="1.0" encoding="UTF-8" ?><rss version="2.0"><channel><title>DryPaper HQ</title><link>https://www.drypaperhq.com</link>'
    for item in db[:10]:
        rss += f'<item><title>{item["name"]}</title><link>https://www.drypaperhq.com/{item["file"]}</link><description>{item["desc"]}</description></item>'
    rss += '</channel></rss>'
    with open("feed.xml", "w") as f: f.write(rss)
update_rss()

# Attack
fresh_leads = hunt_leads()
if fresh_leads:
    print(f"⚔️ ATTACKING {len(fresh_leads)} TARGETS...")
    for lead in fresh_leads:
        send_cold_email(lead, latest['name'], f"https://www.drypaperhq.com/{latest['file']}", latest['price'])

# Report
if os.environ.get("EMAIL_USER"):
    try:
        msg = MIMEMultipart()
        msg['From'] = os.environ.get("EMAIL_USER")
        msg['To'] = TARGET_EMAIL
        msg['Subject'] = f"✅ WAR REPORT: {len(fresh_leads)} VALID EMAILS"
        sent_list = "\n".join(fresh_leads[:5]) if fresh_leads else "No clean leads found."
        body = f"Product: {latest['name']} is LIVE.\n\n🎯 Valid Targets Hit: {len(fresh_leads)}\n\nSample:\n{sent_list}"
        msg.attach(MIMEText(body, 'plain'))
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        s.login(os.environ.get("EMAIL_USER"), os.environ.get("EMAIL_PASS"))
        s.sendmail(os.environ.get("EMAIL_USER"), TARGET_EMAIL, msg.as_string())
        s.quit()
    except: pass

print("✅ DAY COMPLETE.")

