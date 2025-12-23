import json, os, smtplib, requests, random, time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

print("--- 🧠 MARKETING: AI SNIPER MODE (PERSONALIZED) ---")

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

# --- 1. AI ICEBREAKER GENERATOR ---
def generate_icebreaker(name, bio):
    if not GROQ_API_KEY or not bio: 
        return f"I came across your profile on GitHub."
    
    prompt = f"""
    Write a 1-sentence casual icebreaker for a cold email to a developer named {name}.
    His Bio: "{bio}".
    Mention something specific from his bio naturally.
    Keep it short, friendly, and under 20 words. No emojis.
    """
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}]
    }
    try:
        r = requests.post(url, headers=headers, data=json.dumps(payload))
        return r.json()['choices'][0]['message']['content'].strip().replace('"', '')
    except:
        return f"I came across your work on GitHub."

# --- 2. GITHUB USER HUNTER (NOW FETCHES NAME & BIO) ---
def hunt_github_leads():
    print("🕵️ Hunting 50 Leads with BIO data...")
    leads = []
    # Keywords expand kar diye
    keywords = ["agency", "freelancer", "founder", "consultant", "developer", "ceo", "cto", "marketing"]
    
    headers = {"Accept": "application/vnd.github.v3+json"}
    if GH_TOKEN: headers["Authorization"] = f"token {GH_TOKEN}"
    
    # Load existing leads to avoid duplicates
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
                    print(f"   🔍 Scanning batch for '{keyword}'...")
                    for user in data['items']:
                        if len(leads) % 10 == 0: time.sleep(1) # Safety Sleep
                        
                        u_r = requests.get(user['url'], headers=headers)
                        if u_r.status_code == 200:
                            profile = u_r.json()
                            email = profile.get('email')
                            
                            if email and "users.noreply" not in email and email not in existing_emails:
                                # 🔥 GRAB NAME & BIO
                                name = profile.get('name') or profile.get('login')
                                bio = profile.get('bio') or "tech enthusiast"
                                
                                lead_data = {"email": email, "name": name, "bio": bio}
                                print(f"   🎯 TARGET: {email} ({name})")
                                leads.append(lead_data)
                                existing_emails.append(email)
                        
                        if len(leads) >= 50: return leads
        except: pass
        
    return leads

# --- 3. SAVE LEADS ---
def save_leads_to_db(leads):
    if not os.path.exists(LEADS_FILE):
        with open(LEADS_FILE, "w") as f: f.write("email,source,date,status\n")
    with open(LEADS_FILE, "a") as f:
        today = time.strftime("%Y-%m-%d")
        for lead in leads:
            f.write(f"{lead['email']},github,{today},sent\n")
    print(f"💾 Saved {len(leads)} leads to {LEADS_FILE}")

# --- 4. SENDER (PERSONALIZED) ---
def send_cold_email(lead, product_name, price):
    if not SMTP_EMAIL or not SMTP_PASS: return

    email = lead['email']
    name = lead['name']
    bio = lead['bio']

    # 🤖 AI GENERATES CUSTOM LINE
    icebreaker = generate_icebreaker(name, bio)
    print(f"🤖 AI wrote for {name}: {icebreaker}")

    # Spin Content
    closings = ["Best,", "Cheers,", "Regards,", "Talk soon,", "Best regards,"]
    store_link = "https://www.drypaperhq.com"
    subject = f"Quick question about your workflow, {name}?"
    
    body = f"""Hi {name},

{icebreaker}

I noticed you're active in the tech space. I built a specific tool called '{product_name}' that automates manual workflows.
It's currently available for ${price} (Launch Price).

👉 Get it here: {store_link}

{random.choice(closings)}
Rajat
"""
    
    msg = MIMEMultipart()
    msg['From'] = f"Rajat <{SMTP_EMAIL}>"
    msg['To'] = email
    msg['Subject'] = subject
    
    if TARGET_EMAIL:
        msg.add_header('Reply-To', TARGET_EMAIL)
        msg['Bcc'] = TARGET_EMAIL 

    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SMTP_EMAIL, SMTP_PASS)
        server.sendmail(SMTP_EMAIL, [email, TARGET_EMAIL], msg.as_string())
        server.quit()
        print(f"🚀 SENT PERSONALIZED: {email}")
        
        # 🕒 RANDOM SLEEP (20-40 seconds) to fool Gmail Filters
        sleep_time = random.randint(20, 40)
        print(f"   💤 Sleeping {sleep_time}s to avoid spam filters...")
        time.sleep(sleep_time)
        
    except Exception as e:
        print(f"❌ SEND FAILED: {e}")

# --- EXECUTE ---
fresh_leads = hunt_github_leads()
if fresh_leads:
    print(f"⚔️ ATTACKING {len(fresh_leads)} TARGETS...")
    save_leads_to_db(fresh_leads)
    for lead in fresh_leads:
        send_cold_email(lead, latest['name'], latest['price'])
