import requests, json, os, smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

print("--- 🚀 SOCIAL BLAST: OMNI-CHANNEL POSTER ---")

try:
    with open("products.json", "r") as f: product = json.load(f)[0]
except:
    print("❌ No product found.")
    exit()

title = f"New Tool: {product['name']}"
desc = product['desc']
link = "https://www.drypaperhq.com"
price = product['price']
tags = "#AI #SaaS #Agency #Automation"
full_post = f"🚀 {title}\n\n{desc}\n\n💰 Price: ${price}\n👉 Get it here: {link}\n\n{tags}"

# --- 1. TELEGRAM BLAST ---
def post_telegram():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id: return
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": full_post}
    requests.post(url, json=payload)
    print("✅ Posted to Telegram")

# --- 2. DEV.TO BLAST ---
def post_devto():
    key = os.environ.get("DEVTO_API_KEY")
    if not key: return
    data = {"article": {"title": title, "published": True, "body_markdown": f"# {title}\n\n{desc}\n\n### [Get Access Now]({link})", "tags": ["tool", "productivity", "saas"]}}
    requests.post("https://dev.to/api/articles", json=data, headers={"api-key": key})
    print("✅ Posted to Dev.to")

# --- 3. HASHNODE BLAST ---
def post_hashnode():
    token = os.environ.get("HASHNODE_TOKEN")
    pub_id = os.environ.get("HASHNODE_PUB_ID")
    if not token or not pub_id: return
    query = 'mutation CreateStory($input: CreateStoryInput!) { createStory(input: $input) { code success message } }'
    variables = {"input": {"title": title, "contentMarkdown": f"# {title}\n\n{desc}\n\n[Link]({link})", "tags": [{"_id": "56744723958ef13879b9549b", "name": "SaaS", "slug": "saas"}], "publicationId": pub_id}}
    requests.post("https://api.hashnode.com", json={"query": query, "variables": variables}, headers={"Authorization": token})
    print("✅ Posted to Hashnode")

# --- 4. MEDIUM BLAST (NEW) ---
def post_medium():
    token = os.environ.get("MEDIUM_TOKEN")
    if not token: return
    
    # Get User ID
    try:
        user = requests.get("https://api.medium.com/v1/me", headers={"Authorization": f"Bearer {token}"}).json()
        user_id = user['data']['id']
        
        url = f"https://api.medium.com/v1/users/{user_id}/posts"
        data = {
            "title": title,
            "contentFormat": "markdown",
            "content": f"# {title}\n\n{desc}\n\n[Get Access Here]({link})",
            "publishStatus": "public",
            "tags": ["ai", "saas", "technology"]
        }
        requests.post(url, json=data, headers={"Authorization": f"Bearer {token}"})
        print("✅ Posted to Medium")
    except Exception as e: print(f"❌ Medium Failed: {e}")

# --- 5. TUMBLR (VIA EMAIL) ---
def post_tumblr():
    tumblr_email = os.environ.get("TUMBLR_EMAIL") # Secret me daal: yourusername+random@tumblr.com
    smtp_email = os.environ.get("SMTP_EMAIL")
    smtp_pass = os.environ.get("SMTP_PASSWORD")
    
    if not tumblr_email or not smtp_email: return

    msg = MIMEMultipart()
    msg['From'] = smtp_email
    msg['To'] = tumblr_email
    msg['Subject'] = title # Tumblr uses Subject as Title
    msg.attach(MIMEText(f"{desc}\n\n<a href='{link}'>Get Access</a>\n\n{tags}", 'html'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(smtp_email, smtp_pass)
        server.sendmail(smtp_email, tumblr_email, msg.as_string())
        server.quit()
        print("✅ Posted to Tumblr (via Email)")
    except Exception as e: print(f"❌ Tumblr Failed: {e}")

# --- 6. TELEGRAPH (Instant View) ---
def post_telegraph():
    # Telegraph doesn't need auth for creating, but better to save token if editing.
    # We will do 'Anonymous' creation for speed.
    content = [{"tag": "p", "children": [desc]}, {"tag": "a", "attrs": {"href": link}, "children": ["Get Access Now"]}]
    data = {
        "title": title,
        "author_name": "DryPaper HQ",
        "content": json.dumps(content),
        "return_content": False
    }
    requests.post("https://api.telegra.ph/createPage", data=data)
    print("✅ Posted to Telegra.ph")

# EXECUTE ALL
post_telegram()
post_devto()
post_hashnode()
post_medium()
post_tumblr()
post_telegraph()

