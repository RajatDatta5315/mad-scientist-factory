import json, os, smtplib, requests, random, time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

print("--- 🧠 MARKETING: AI SNIPER MODE (SAFE LIMIT 40) ---")

SMTP_EMAIL = os.environ.get("SMTP_EMAIL")
SMTP_PASS = os.environ.get("SMTP_PASSWORD")
TARGET_EMAIL = os.environ.get("TARGET_EMAIL")
GH_TOKEN = os.environ.get("GITHUB_TOKEN") 
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

DB_FILE = "products.json"
LEADS_FILE = "leads.csv"

if not os.path.exists(DB_FILE):
    print("⚠️ DB Missing. Skipping.")
    exit()

with open(DB_FILE, "r") as f: db = json.load(f)
latest = db[0]

def generate_icebreaker(name, bio):
    if not GROQ_API_KEY or not bio: 
        return f"I came across your profile on GitHub."
    prompt = f"Write a 1-sentence casual icebreaker for a developer named {name}. Bio: '{bio}'. Keep it short, friendly, no emojis."
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}]}
    try:
        return requests.post(url, headers=headers, data=json.dumps(payload)).json()['choices'][0]['message']['content'].strip().replace('"', '')
    except:
        return f"I came across your work on GitHub."

def hunt_github_leads():
    print("🕵️ Hunting Leads...")
    leads = []
    keywords = ["agency", "freelancer", "founder", "consultant", "developer", "ceo", "cto", "marketing"]
    headers = {"Accept": "application/vnd.github.v3+json"}
    if GH_TOKEN: headers["Authorization"] = f"token {GH_TOKEN}"
    
    existing_emails = []
    if os.path.exists(LEADS_FILE):
        with open(LEADS_FILE, "r") as f:
            existing_emails = [line.split(",")[0] for line in f.readlines()]

    for _ in range(5): 
        keyword = random.choice(keywords)
        url = f"https://api.github.com/search/users?q={keyword}+is:hireable&per_page=100&sort=updated"
        try:
            r = requests.get(url, headers=headers)
            if r.status_code == 200:
                data = r.json()
                if "items" in data:
                    print(f"   🔍 Scanning for '{keyword}'...")
                    for user in data['items']:
                        if len(leads) % 10 == 0: time.sleep(1)
                        u_r = requests.get(user['url'], headers=headers)
                        if u_r.status_code == 200:
                            profile = u_r.json()
                            email = profile.get('email')
                            if email and "users.noreply" not in email and email not in existing_emails:
                                name = profile.get('name') or profile.get('login')
                                bio = profile.get('bio') or "tech enthusiast"
                                lead_data = {"email": email, "name": name, "bio": bio}
                                print(f"   🎯 TARGET: {email}")
                                leads.append(lead_data)
                                existing_emails.append(email)
                        
                        # 🔥 STRICT LIMIT INCREASED TO 40
                        if len(leads) >= 40: return leads
        except: pass
    return leads

def save_leads_to_db(leads):
    if not os.path.exists(LEADS_FILE):
        with open(LEADS_FILE, "w") as f: f.write("email,source,date,status\n")
    with open(LEADS_FILE, "a") as f:
        today = time.strftime("%Y-%m-%d")
        for lead in leads:
            f.write(f"{lead['email']},github,{today},sent\n")
    print(f"💾 Saved {len(leads)} leads to {LEADS_FILE}")

def send_cold_email(lead, product_name, price):
    if not SMTP_EMAIL or not SMTP_PASS: return
    email = lead['email']
    name = lead['name']
    icebreaker = generate_icebreaker(name, lead['bio'])
    print(f"🤖 AI wrote for {name}: {icebreaker}")

    store_link = "https://www.drypaperhq.com"
    subject = f"Quick question about your workflow, {name}?"
    body = f"""Hi {name},\n\n{icebreaker}\n\nI noticed you're active in the tech space. I built a specific tool called '{product_name}' that automates manual workflows.\nIt's currently available for ${price} (Launch Price).\n\n👉 Get it here: {store_link}\n\nBest regards,\nRajat"""
    
    msg = MIMEMultipart()
    msg['From'] = f"Rajat <{SMTP_EMAIL}>"
    msg['To'] = email
    msg['Subject'] = subject
    if TARGET_EMAIL: msg.add_header('Reply-To', TARGET_EMAIL); msg['Bcc'] = TARGET_EMAIL 
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SMTP_EMAIL, SMTP_PASS)
        server.sendmail(SMTP_EMAIL, [email, TARGET_EMAIL], msg.as_string())
        server.quit()
        print(f"🚀 SENT: {email}")
        time.sleep(random.randint(20, 40))
    except Exception as e:
        print(f"❌ SEND FAILED: {e}")

fresh_leads = hunt_github_leads()
if fresh_leads:
    print(f"⚔️ ATTACKING {len(fresh_leads)} TARGETS...")
    save_leads_to_db(fresh_leads)
    for lead in fresh_leads:
        send_cold_email(lead, latest['name'], latest['price'])

