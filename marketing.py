import json, os, smtplib, requests, random, time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

print("--- 🏴‍☠️ MARKETING: MAX VOLUME (50/DAY) ---")

SMTP_EMAIL = os.environ.get("SMTP_EMAIL")
SMTP_PASS = os.environ.get("SMTP_PASSWORD")
TARGET_EMAIL = os.environ.get("TARGET_EMAIL")
GH_TOKEN = os.environ.get("GITHUB_TOKEN") 

DB_FILE = "products.json"
LEADS_FILE = "leads.csv"

if not os.path.exists(DB_FILE):
    print("⚠️ DB Missing. Skipping.")
    exit()

with open(DB_FILE, "r") as f: db = json.load(f)
latest = db[0]

# --- 1. SAVE LEADS TO CSV ---
def save_leads_to_db(leads):
    if not os.path.exists(LEADS_FILE):
        with open(LEADS_FILE, "w") as f: f.write("email,source,date,status\n")
    with open(LEADS_FILE, "a") as f:
        today = time.strftime("%Y-%m-%d")
        for email in leads:
            f.write(f"{email},github,{today},sent\n")
    print(f"💾 Saved {len(leads)} leads to {LEADS_FILE}")

# --- 2. GITHUB USER HUNTER (EXPANDED) ---
def hunt_github_leads():
    print("🕵️ Hunting 50 Leads...")
    leads = []
    # Keywords expand kar diye taaki zyada log milein
    keywords = ["agency", "freelancer", "founder", "consultant", "developer", "ceo", "cto", "marketing"]
    
    headers = {"Accept": "application/vnd.github.v3+json"}
    if GH_TOKEN: headers["Authorization"] = f"token {GH_TOKEN}"
    
    # Loop taaki agar ek keyword se kam mile to dusra try kare
    for _ in range(5): 
        keyword = random.choice(keywords)
        url = f"https://api.github.com/search/users?q={keyword}+is:hireable&per_page=100&sort=updated"
        
        try:
            r = requests.get(url, headers=headers)
            if r.status_code == 200:
                data = r.json()
                if "items" in data:
                    print(f"   🔍 Scanning batch for '{keyword}'...")
                    for user in data['items']:
                        # Thora random sleep taaki GitHub block na kare
                        if len(leads) % 10 == 0: time.sleep(1)
                        
                        u_r = requests.get(user['url'], headers=headers)
                        if u_r.status_code == 200:
                            email = u_r.json().get('email')
                            if email and "users.noreply" not in email and email not in leads:
                                print(f"   🎯 TARGET: {email}")
                                leads.append(email)
                        
                        # 🔥 TARGET: 50 EMAILS
                        if len(leads) >= 50: return list(set(leads))
        except: pass
        
    return list(set(leads))

# --- 3. SENDER ---
def send_cold_email(to_email, product_name, price):
    if not SMTP_EMAIL or not SMTP_PASS: return

    # LINK TO STORE (No Freebies)
    store_link = "https://www.drypaperhq.com"
    
    subject = f"Tool for your agency: {product_name}"
    body = f"""Hi,

I saw your profile on GitHub and noticed you run an agency/tech business.

I built a specific tool called '{product_name}' that automates workflow.
It's currently available for ${price} (Launch Price).

👉 Get it here: {store_link}

Best,
Rajat
"""
    
    msg = MIMEMultipart()
    msg['From'] = f"Rajat <{SMTP_EMAIL}>"
    msg['To'] = to_email
    msg['Subject'] = subject
    
    # Reply tere paas aayega, aur Copy bhi
    if TARGET_EMAIL:
        msg.add_header('Reply-To', TARGET_EMAIL)
        msg['Bcc'] = TARGET_EMAIL 

    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SMTP_EMAIL, SMTP_PASS)
        server.sendmail(SMTP_EMAIL, [to_email, TARGET_EMAIL], msg.as_string())
        server.quit()
        print(f"🚀 SENT SUCCESS: {to_email}")
        time.sleep(2) # Thora break taaki spam na lage
    except Exception as e:
        print(f"❌ SEND FAILED: {e}")

# --- EXECUTE ---
fresh_leads = hunt_github_leads()
if fresh_leads:
    print(f"⚔️ ATTACKING {len(fresh_leads)} TARGETS...")
    save_leads_to_db(fresh_leads)
    for lead in fresh_leads:
        send_cold_email(lead, latest['name'], latest['price'])

