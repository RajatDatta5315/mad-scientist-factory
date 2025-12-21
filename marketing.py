import json, os, smtplib, requests, random, time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

print("--- 🏴‍☠️ MARKETING: GITHUB EMAIL SNIPER ---")

SMTP_EMAIL = os.environ.get("SMTP_EMAIL")
SMTP_PASS = os.environ.get("SMTP_PASSWORD")
TARGET_EMAIL = os.environ.get("TARGET_EMAIL")
# GitHub Token (Automatically provided by Actions usually, or limits are 60/hr)
GH_TOKEN = os.environ.get("GITHUB_TOKEN") 

DB_FILE = "products.json"
if not os.path.exists(DB_FILE): exit()
with open(DB_FILE, "r") as f: db = json.load(f)
latest = db[0]

# --- 1. GITHUB USER HUNTER ---
def hunt_github_leads():
    print("🕵️ Sniping Emails from GitHub Users...")
    leads = []
    
    keywords = ["agency", "founder", "freelancer", "developer"]
    keyword = random.choice(keywords)
    
    # Search for users with keyword in bio
    # Sort by joined (newest) or followers
    url = f"https://api.github.com/search/users?q={keyword}+type:user&per_page=30&sort=joined&order=desc"
    
    headers = {"Accept": "application/vnd.github.v3+json"}
    if GH_TOKEN: headers["Authorization"] = f"token {GH_TOKEN}"
    
    try:
        r = requests.get(url, headers=headers)
        data = r.json()
        
        if "items" in data:
            print(f"   found {len(data['items'])} potential targets. Scanning profiles...")
            for user in data['items']:
                # Fetch detailed profile to get email
                u_url = user['url']
                u_r = requests.get(u_url, headers=headers)
                u_data = u_r.json()
                
                email = u_data.get('email')
                if email:
                    print(f"   🎯 Got one: {email}")
                    leads.append(email)
                time.sleep(0.5) # Be gentle with API
    except Exception as e:
        print(f"❌ GitHub API Error: {e}")
        
    return list(set(leads))[:20]

# --- 2. SENDER ---
def send_cold_email(to_email, product_name, product_link, price):
    if not SMTP_EMAIL or not SMTP_PASS: return
    
    # Simple, direct script for developers/agencies
    subject = f"Tool for your projects: {product_name}"
    body = f"Hi,\n\nFound your profile on GitHub.\n\nI built a utility called {product_name} that automates workflow.\nIt's a pure JS tool (no bloat).\n\nCheck it out: {product_link}\n\nCheers,\nRajat"
    
    msg = MIMEMultipart()
    msg['From'] = f"Rajat <{SMTP_EMAIL}>"
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP_SSL('smtp.hostinger.com', 465)
        server.login(SMTP_EMAIL, SMTP_PASS)
        server.sendmail(SMTP_EMAIL, to_email, msg.as_string())
        server.quit()
        print(f"🚀 SENT TO: {to_email}")
        time.sleep(2)
    except: pass

# --- EXECUTE ---
fresh_leads = hunt_github_leads()

if fresh_leads:
    print(f"⚔️ ATTACKING {len(fresh_leads)} GITHUB DEVS...")
    for lead in fresh_leads:
        send_cold_email(lead, latest['name'], f"https://www.drypaperhq.com/{latest['file']}", latest['price'])

# REPORT
if os.environ.get("EMAIL_USER"):
    try:
        msg = MIMEMultipart()
        msg['From'] = os.environ.get("EMAIL_USER")
        msg['To'] = TARGET_EMAIL
        msg['Subject'] = f"✅ GITHUB RAID REPORT: {len(fresh_leads)} EMAILS"
        body = f"Source: GitHub User Search\nTargets Hit: {len(fresh_leads)}\n\n(These are real developer/agency emails from their profiles.)"
        msg.attach(MIMEText(body, 'plain'))
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        s.login(os.environ.get("EMAIL_USER"), os.environ.get("EMAIL_PASS"))
        s.sendmail(os.environ.get("EMAIL_USER"), TARGET_EMAIL, msg.as_string())
        s.quit()
    except: pass


