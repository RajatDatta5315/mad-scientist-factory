import json, os, smtplib, requests, random, time, datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

print("--- 🧠 MARKETING: WOLF MODE (LIMIT 40) ---")

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

# --- AGGRESSIVE PSYCHOLOGY GENERATOR ---
def generate_killer_hook(name, bio, product_name):
    if not GROQ_API_KEY: 
        return f"Stop wasting time on manual tasks. {product_name} fixes it."
    
    # ROTATING STRATEGIES (A/B Testing)
    strategies = [
        "Pain Agitation", # "You are losing money..."
        "Authority",      # "Top agencies use this..."
        "Direct Value",   # "Save 10 hours/week..."
        "FOMO"            # "Launch price ending soon..."
    ]
    strategy = random.choice(strategies)
    
    prompt = f"""
    Write a 1-sentence aggressive, high-converting opening line for a cold email to {name}.
    His Bio: "{bio}".
    Product: "{product_name}" (Automation Tool).
    STRATEGY: {strategy}.
    Rule: Be direct, confident, and slightly provocative. No fluff. No "I hope you are well".
    """
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}]}
    try:
        return requests.post(url, headers=headers, data=json.dumps(payload)).json()['choices'][0]['message']['content'].strip().replace('"', '')
    except:
        return f"I saw your GitHub. You are building great things, but your workflow is slow."

def hunt_github_leads():
    print("🕵️ Hunting High-Value Targets...")
    leads = []
    keywords = ["agency", "freelancer", "founder", "cto", "tech lead", "architect"] # High paying keywords
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
                    print(f"   🔍 Scanning sector: '{keyword}'...")
                    for user in data['items']:
                        if len(leads) % 10 == 0: time.sleep(1)
                        u_r = requests.get(user['url'], headers=headers)
                        if u_r.status_code == 200:
                            profile = u_r.json()
                            email = profile.get('email')
                            if email and "users.noreply" not in email and email not in existing_emails:
                                name = profile.get('name') or profile.get('login')
                                bio = profile.get('bio') or "Tech Professional"
                                leads.append({"email": email, "name": name, "bio": bio})
                                existing_emails.append(email)
                                print(f"   🎯 LOCKED TARGET: {email}")
                        
                        # 🔥 LIMIT INCREASED TO 40
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

def send_cold_email(lead, product_name, price):
    if not SMTP_EMAIL or not SMTP_PASS: return
    email = lead['email']
    name = lead['name']
    
    # 🧠 GENERATE KILLER HOOK
    hook = generate_killer_hook(name, lead['bio'], product_name)
    print(f"🤖 AI Sniper: {hook}")

    store_link = "https://www.drypaperhq.com"
    subject = f"Tool to automate your workflow (Launch Deal)"
    
    body = f"""{name},

{hook}

I built '{product_name}' specifically to kill manual work for developers like you.
It's currently ${price} (Launch Price). The price doubles next week.

Don't waste time.
👉 Grab it here: {store_link}

Rajat
Founder, DryPaper HQ
"""
    
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
        print(f"🚀 FIRED AT: {email}")
        time.sleep(random.randint(15, 30)) # Faster fire rate
    except Exception as e:
        print(f"❌ MISFIRE: {e}")

fresh_leads = hunt_github_leads()
if fresh_leads:
    print(f"⚔️ ENGAGING {len(fresh_leads)} HOSTILES...")
    save_leads_to_db(fresh_leads)
    for lead in fresh_leads:
        send_cold_email(lead, latest['name'], latest['price'])

