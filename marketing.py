import json, os, smtplib, requests, random, time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

print("--- 🏴‍☠️ MARKETING: DEBUG MODE ---")

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

# --- 1. GITHUB USER HUNTER ---
def hunt_github_leads():
    print("🕵️ Hunting Leads...")
    leads = []
    keywords = ["agency", "freelancer", "founder", "consultant"]
    keyword = random.choice(keywords)
    
    url = f"https://api.github.com/search/users?q={keyword}+is:hireable&per_page=40&sort=updated"
    headers = {"Accept": "application/vnd.github.v3+json"}
    if GH_TOKEN: headers["Authorization"] = f"token {GH_TOKEN}"
    
    try:
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            data = r.json()
            if "items" in data:
                print(f"   🔍 Scanning {len(data['items'])} profiles...")
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

# --- 2. SENDER (WITH ERROR LOGGING) ---
def send_cold_email(to_email, product_name, product_link, price):
    # Check Credentials
    if not SMTP_EMAIL:
        print("❌ ERROR: SMTP_EMAIL secret missing!")
        return
    if not SMTP_PASS:
        print("❌ ERROR: SMTP_PASSWORD secret missing!")
        return

    subject = f"Tool for your dev workflow: {product_name}"
    body = f"Hi,\n\nI built {product_name} to speed up workflow.\nCheck it out: {product_link}\n\nCheers,\nRajat"
    
    msg = MIMEMultipart()
    msg['From'] = f"Rajat <{SMTP_EMAIL}>"
    msg['To'] = to_email
    msg['Subject'] = subject
    
    if TARGET_EMAIL:
        msg.add_header('Reply-To', TARGET_EMAIL)
        msg['Bcc'] = TARGET_EMAIL 

    msg.attach(MIMEText(body, 'plain'))
    
    try:
        # Connecting...
        print(f"🔌 Connecting to SMTP for {to_email}...")
        server = smtplib.SMTP('smtp.gmail.com', 587) # GMAIL PORT CHANGE (Try 587 first)
        server.starttls()
        server.login(SMTP_EMAIL, SMTP_PASS)
        server.sendmail(SMTP_EMAIL, [to_email, TARGET_EMAIL], msg.as_string())
        server.quit()
        print(f"🚀 SENT SUCCESS: {to_email}")
        time.sleep(2)
    except Exception as e:
        print(f"❌ SEND FAILED: {e}") # <--- YE ERROR BATAYEGA KYU FAIL HUA

# --- EXECUTE ---
fresh_leads = hunt_github_leads()
if fresh_leads:
    print(f"⚔️ ATTACKING {len(fresh_leads)} TARGETS...")
    for lead in fresh_leads:
        send_cold_email(lead, latest['name'], f"https://www.drypaperhq.com/{latest['file']}", latest['price'])

