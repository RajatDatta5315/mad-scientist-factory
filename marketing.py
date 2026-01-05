import json, os, smtplib, requests, random, time, re
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import dns.resolver # REQUIREMENT: pip install dnspython

print("--- 🧠 MARKETING: SNIPER VALIDATION MODE ---")

SMTP_EMAIL = os.environ.get("SMTP_EMAIL")
SMTP_PASS = os.environ.get("SMTP_PASSWORD")
TARGET_EMAIL = os.environ.get("TARGET_EMAIL")
GH_TOKEN = os.environ.get("GITHUB_TOKEN") 
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

DB_FILE = "products.json"
LEADS_FILE = "leads.csv"

# --- EMAIL VALIDATION ENGINE ---
def is_valid_email(email):
    # 1. Regex Format Check
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return False
    
    # 2. Block GitHub Noreply & Common Bots
    if "noreply" in email or "bot" in email or "example" in email:
        return False
        
    # 3. Domain MX Record Check (Is the domain real?)
    domain = email.split('@')[1]
    try:
        records = dns.resolver.resolve(domain, 'MX')
        return True
    except:
        return False

# --- AI HOOK GENERATOR (SOFT CTA) ---
def generate_soft_hook(name, bio, product_name):
    if not GROQ_API_KEY: 
        return f"I built {product_name} to help devs like you."
    
    prompt = f"""
    Write a cold email opening for {name}. Bio: "{bio}".
    Product: "{product_name}".
    Goal: Start a conversation, NOT a hard sell.
    Tone: Peer-to-peer developer, casual, low pressure.
    Output: Just the first 2 sentences.
    """
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}]}
    try:
        return requests.post(url, headers=headers, data=json.dumps(payload)).json()['choices'][0]['message']['content'].strip().replace('"', '')
    except:
        return f"Saw your work on GitHub. Impressive stuff."

# --- LEAD HUNTING (WITH VALIDATION) ---
def hunt_github_leads():
    print("🕵️ Hunting Validated Targets...")
    leads = []
    keywords = ["founder", "cto", "tech lead", "architect", "senior engineer"] 
    locations = ["USA", "San Francisco", "New York", "London", "Berlin", "Canada"]
    
    headers = {"Accept": "application/vnd.github.v3+json"}
    if GH_TOKEN: headers["Authorization"] = f"token {GH_TOKEN}"
    
    existing_emails = []
    if os.path.exists(LEADS_FILE):
        with open(LEADS_FILE, "r") as f:
            existing_emails = [line.split(",")[0] for line in f.readlines()]

    for _ in range(3): # Reduce loops to focus on quality
        keyword = random.choice(keywords)
        location = random.choice(locations)
        query = f"{keyword} location:\"{location}\" is:hireable"
        url = f"https://api.github.com/search/users?q={query}&per_page=50&sort=updated" # Reduced per_page
        
        try:
            r = requests.get(url, headers=headers)
            if r.status_code == 200:
                data = r.json()
                if "items" in data:
                    for user in data['items']:
                        if len(leads) % 5 == 0: time.sleep(1)
                        u_r = requests.get(user['url'], headers=headers)
                        if u_r.status_code == 200:
                            profile = u_r.json()
                            email = profile.get('email')
                            
                            # 🔥 VALIDATION CHECK
                            if email and email not in existing_emails:
                                if is_valid_email(email):
                                    name = profile.get('name') or profile.get('login')
                                    bio = profile.get('bio') or "Dev"
                                    leads.append({"email": email, "name": name, "bio": bio})
                                    existing_emails.append(email)
                                    print(f"   ✅ VERIFIED LEAD: {email}")
                                else:
                                    print(f"   🗑️ INVALID EMAIL: {email}")
                        
                        if len(leads) >= 20: return leads # Reduced daily limit to 20 for safety
        except: pass
    return leads

def save_leads(leads):
    if not os.path.exists(LEADS_FILE):
        with open(LEADS_FILE, "w") as f: f.write("email,source,date,status\n")
    with open(LEADS_FILE, "a") as f:
        today = time.strftime("%Y-%m-%d")
        for lead in leads:
            f.write(f"{lead['email']},github,{today},sent\n")

def send_mail(lead, product):
    if not SMTP_EMAIL or not SMTP_PASS: return
    email = lead['email']
    name = lead['name']
    
    hook = generate_soft_hook(name, lead['bio'], product['name'])
    
    # SOFT SELL TEMPLATE
    subject = f"Question about your workflow, {name}"
    body = f"""Hi {name},

{hook}

I'm building an automation tool called {product['name']} and looking for feedback from senior devs.
It handles the boring stuff so you can focus on code.

Would you be open to checking it out? No pressure.
Link: https://www.drypaperhq.com

Cheers,
Rajat
"""
    
    msg = MIMEMultipart()
    msg['From'] = f"Rajat <{SMTP_EMAIL}>"
    msg['To'] = email
    msg['Subject'] = subject
    if TARGET_EMAIL: msg['Bcc'] = TARGET_EMAIL 
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SMTP_EMAIL, SMTP_PASS)
        server.sendmail(SMTP_EMAIL, [email, TARGET_EMAIL], msg.as_string())
        server.quit()
        print(f"🚀 SENT: {email}")
        time.sleep(random.randint(30, 60)) # Increased sleep for safety
    except Exception as e:
        print(f"❌ ERROR: {e}")

# --- EXECUTION ---
with open(DB_FILE, "r") as f: db = json.load(f)
latest = db[0]

fresh_leads = hunt_github_leads()
if fresh_leads:
    print(f"⚔️ ENGAGING {len(fresh_leads)} VERIFIED LEADS...")
    save_leads(fresh_leads)
    for lead in fresh_leads:
        send_mail(lead, latest)

