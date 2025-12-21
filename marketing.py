import json, os, smtplib, requests, random
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

print("--- 📢 MARKETING: SALES DEPARTMENT ---")

DEVTO_KEY = os.environ.get("DEVTO_API_KEY")
DB_FILE = "products.json"

if not os.path.exists(DB_FILE):
    print("⚠️ No products found. Marketing sleeping.")
    exit()

with open(DB_FILE, "r") as f: db = json.load(f)
latest = db[0]

# --- 1. LEAD HUNTER (MANUAL TRIGGER) ---
def get_lead_query(product_name):
    # Ye tujhe Google pe paste karna hai. Ye hidden emails nikalega.
    dork = f'site:linkedin.com/in/ "gmail.com" "founder" AND "{product_name.split()[0]}"'
    return dork

# --- 2. RSS FEED GENERATOR (FOR IFTTT/ZAPIER) ---
# Ye file 'feed.xml' banayegi. Ise IFTTT me jodna hai.
def update_rss():
    rss = '<?xml version="1.0" encoding="UTF-8" ?><rss version="2.0"><channel><title>DryPaper HQ</title><link>https://www.drypaperhq.com</link><description>Premium Tools</description>'
    for item in db[:10]:
        rss += f'<item><title>{item["name"]}</title><link>https://www.drypaperhq.com/{item["file"]}</link><description>{item["desc"]}</description><guid>{item["name"]}</guid><pubDate>Mon, 01 Jan 2024 00:00:00 GMT</pubDate></item>'
    rss += '</channel></rss>'
    with open("feed.xml", "w") as f: f.write(rss)
    print("✅ RSS Feed Updated for Automation.")

# --- 3. DEV.TO POSTER ---
def post_devto():
    if not DEVTO_KEY: return
    body = f"# {latest['name']}\n\nAgencies need speed. We built {latest['name']} to help you scale.\n\n## Features\n- Automated Workflow\n- Dark Mode UI\n- PDF Export\n\n[Get it here for ${latest['price']}](https://www.drypaperhq.com/{latest['file']})"
    try:
        requests.post("https://dev.to/api/articles", headers={"api-key": DEVTO_KEY, "Content-Type": "application/json"}, json={"article": {"title": f"Launch: {latest['name']}", "body_markdown": body, "published": True, "tags": ["productivity", "agency"]}})
        print("✅ Posted on Dev.to")
    except: print("❌ Dev.to Failed")

# EXECUTE
update_rss()
post_devto()

# --- 4. BOSS REPORT (EMAIL) ---
if os.environ.get("EMAIL_USER"):
    dork = get_lead_query(latest['name'])
    msg = MIMEMultipart()
    msg['From'] = os.environ.get("EMAIL_USER")
    msg['To'] = os.environ.get("TARGET_EMAIL")
    msg['Subject'] = f"💰 SALES READY: {latest['name']}"
    
    body = f"""
    BOSS, NEW ASSET DEPLOYED.
    
    🚀 Product: {latest['name']}
    🌐 RSS Feed Updated (Socials will auto-post via IFTTT)
    
    ----- LEAD GENERATION STRATEGY -----
    Step 1: Copy this code below.
    Step 2: Paste in Google Search.
    Step 3: Collect Emails.
    
    CODE: {dork}
    
    ------------------------------------
    """
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        s.login(os.environ.get("EMAIL_USER"), os.environ.get("EMAIL_PASS"))
        s.sendmail(os.environ.get("EMAIL_USER"), os.environ.get("TARGET_EMAIL"), msg.as_string())
        s.quit()
        print("✅ Report Sent")
    except: pass
