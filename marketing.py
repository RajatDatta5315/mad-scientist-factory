import json, os, smtplib, requests, random, time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

print("--- 🏴‍☠️ MARKETING: GITHUB ELITE SNIPER (REPLY-TO FIXED) ---")

SMTP_EMAIL = os.environ.get("SMTP_EMAIL")
SMTP_PASS = os.environ.get("SMTP_PASSWORD")
TARGET_EMAIL = os.environ.get("TARGET_EMAIL") # Ye tera Personal Gmail hai
GH_TOKEN = os.environ.get("GITHUB_TOKEN") 

DB_FILE = "products.json"
LEADS_FILE = "leads.csv"

# Fallback
if not os.path.exists(DB_FILE):
    print("⚠️ DB Missing. Skipping.")
    exit()

with open(DB_FILE, "r") as f: db = json.load(f)
latest = db[0]

# --- 0. SAVE LEADS TO CSV ---
def save_leads_to_db(leads):
    if not os.path.exists(LEADS_FILE):
        with open(LEADS_FILE, "w") as f: f.write("email,source,date,status\n")
    
    with open(LEADS_FILE, "a") as f:
        today = time.strftime("%Y-%m-%d")
        for email in leads:
            f.write(f"{email},github,{today},sent\n")
    print(f"💾 Saved {len(leads)} leads to {LEADS_FILE}")

# --- 1. GITHUB USER HUNTER ---
def hunt_github_leads():
    print("🕵️ Sniping 'Hireable' Users on GitHub...")
    leads = []
    keywords = ["agency", "freelancer", "fullstack", "founder", "consultant"]
    keyword = random.choice(keywords)
    
    url = f"https://api.github.com/search/users?q={keyword}+is:hireable&per_page=40&sort=updated"
    headers = {"Accept": "application/vnd.github.v3+json"}
    if GH_TOKEN: headers["Authorization"] = f"token {GH_TOKEN}"
    
    try:
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            data = r.json()
            if "items" in data:
                print(f"   🔍 Scanning {len(data['items'])} profiles for {keyword}...")
                for user in data['items']:
                    u_r = requests.get(user['url'], headers=headers)
                    if u_r.status_code == 200:
                        email = u_r.json().get('email')
                        if email and "users.noreply" not in email:
                            print(f"   🎯 TARGET: {email}")
                            leads.append(email)
                    if len(leads) >= 15: break 
    except Exception as e: print(f"❌ Error: {e}")
    return list(set(leads))

# --- 2. SENDER (WITH REPLY-TO FIX) ---
def send_cold_email(to_email, product_name, product_link, price):
    if not SMTP_EMAIL or not SMTP_PASS: return
    
    subject = f"Tool for your dev workflow: {product_name}"
    body = f"Hi,\n\nSaw your GitHub profile.\n\nI built a utility called {product_name} to speed up workflow.\n\nCheck it out: {product_link}\n\nCheers,\nRajat"
    
    msg = MIMEMultipart()
    msg['From'] = f"Rajat <{SMTP_EMAIL}>"
    msg['To'] = to_email
    msg['Subject'] = subject
    
    # 🔥 MAGIC LINE: Reply seedha tere Gmail pe aayega
    if TARGET_EMAIL:
        msg.add_header('Reply-To', TARGET_EMAIL)

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
    print(f"⚔️ ATTACKING {len(fresh_leads)} TARGETS...")
    save_leads_to_db(fresh_leads)
    for lead in fresh_leads:
        send_cold_email(lead, latest['name'], f"https://www.drypaperhq.com/{latest['file']}", latest['price'])

# REPORT
if os.environ.get("EMAIL_USER"):
    try:
        msg = MIMEMultipart()
        msg['From'] = os.environ.get("EMAIL_USER")
        msg['To'] = TARGET_EMAIL
        msg['Subject'] = f"✅ SUCCESS: {len(fresh_leads)} EMAILS SENT"
        body = f"Product: {latest['name']}\nLeads Hit: {len(fresh_leads)}\n\n(Replies will come to this email)."
        msg.attach(MIMEText(body, 'plain'))
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        s.login(os.environ.get("EMAIL_USER"), os.environ.get("EMAIL_PASS"))
        s.sendmail(os.environ.get("EMAIL_USER"), TARGET_EMAIL, msg.as_string())
        s.quit()
    except: pass

