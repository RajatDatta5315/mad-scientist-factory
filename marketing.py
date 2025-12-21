import json, os, smtplib, requests, random, time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

print("--- 🏴‍☠️ MARKETING: GITHUB ELITE SNIPER ---")

SMTP_EMAIL = os.environ.get("SMTP_EMAIL")
SMTP_PASS = os.environ.get("SMTP_PASSWORD")
TARGET_EMAIL = os.environ.get("TARGET_EMAIL")
GH_TOKEN = os.environ.get("GITHUB_TOKEN") 

DB_FILE = "products.json"
# Fallback if DB missing
if not os.path.exists(DB_FILE):
    print("⚠️ DB Missing. Skipping.")
    exit()

with open(DB_FILE, "r") as f: db = json.load(f)
latest = db[0]

# --- 1. GITHUB USER HUNTER (HIREABLE ONLY) ---
def hunt_github_leads():
    print("🕵️ Sniping 'Hireable' Users on GitHub...")
    leads = []
    
    # Target Keywords: Log jo agencies chalate hain ya freelance karte hain
    keywords = ["agency", "freelancer", "fullstack", "founder", "consultant"]
    keyword = random.choice(keywords)
    
    # URL: Search Users + Is:Hireable (High Email Success Rate)
    url = f"https://api.github.com/search/users?q={keyword}+is:hireable&per_page=40&sort=updated"
    
    headers = {"Accept": "application/vnd.github.v3+json"}
    if GH_TOKEN: 
        headers["Authorization"] = f"token {GH_TOKEN}"
        print("✅ Authenticated Mode: ON (Unlimited Power)")
    else:
        print("⚠️ Warning: No Token Found. Rate Limits may apply.")
    
    try:
        r = requests.get(url, headers=headers)
        if r.status_code != 200:
            print(f"❌ API Error: {r.status_code} - {r.text}")
            return []
            
        data = r.json()
        
        if "items" in data:
            print(f"   🔍 Scanning {len(data['items'])} profiles for {keyword}...")
            for user in data['items']:
                # Profile fetch kar ke email check karo
                u_url = user['url']
                u_r = requests.get(u_url, headers=headers)
                if u_r.status_code == 200:
                    u_data = u_r.json()
                    email = u_data.get('email')
                    
                    if email and "users.noreply" not in email:
                        print(f"   🎯 TARGET ACQUIRED: {email}")
                        leads.append(email)
                
                if len(leads) >= 15: break # Daily Quota
                
    except Exception as e:
        print(f"❌ Critical Error: {e}")
        
    return list(set(leads))

# --- 2. SENDER ---
def send_cold_email(to_email, product_name, product_link, price):
    if not SMTP_EMAIL or not SMTP_PASS: return
    
    subject = f"Tool for your dev workflow: {product_name}"
    body = f"Hi,\n\nSaw your GitHub profile (Hireable status).\n\nI built a no-nonsense utility called {product_name}.\nIt's a single-file tool designed to speed up your work.\n\nCheck it out: {product_link}\n\nCheers,\nRajat"
    
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
    print(f"⚔️ ATTACKING {len(fresh_leads)} TARGETS...")
    for lead in fresh_leads:
        send_cold_email(lead, latest['name'], f"https://www.drypaperhq.com/{latest['file']}", latest['price'])

# REPORT
if os.environ.get("EMAIL_USER"):
    try:
        msg = MIMEMultipart()
        msg['From'] = os.environ.get("EMAIL_USER")
        msg['To'] = TARGET_EMAIL
        msg['Subject'] = f"✅ SUCCESS: {len(fresh_leads)} REAL EMAILS"
        body = f"Product: {latest['name']}\n\n🎯 Real GitHub Leads Hit: {len(fresh_leads)}\n\nMode: Authenticated (High Success)"
        msg.attach(MIMEText(body, 'plain'))
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        s.login(os.environ.get("EMAIL_USER"), os.environ.get("EMAIL_PASS"))
        s.sendmail(os.environ.get("EMAIL_USER"), TARGET_EMAIL, msg.as_string())
        s.quit()
    except: pass

