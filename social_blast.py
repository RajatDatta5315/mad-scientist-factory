import requests, json, os, praw, tweepy

print("--- 🚀 SOCIAL BLAST: AUTO POSTER ---")

try:
    with open("products.json", "r") as f: product = json.load(f)[0]
except: exit()

title = f"New Tool: {product['name']}"
desc = product['desc']
link = f"https://www.drypaperhq.com"
price = product['price']
tags = "#AI #SaaS #Agency #Automation"
full_post = f"🚀 {title}\n\n{desc}\n\n💰 Price: ${price}\n👉 Get it here: {link}\n\n{tags}"

# --- 1. TELEGRAM BLAST (NEW) ---
def post_telegram():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id: return
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": full_post}
    r = requests.post(url, json=payload)
    if r.status_code == 200: print("✅ Posted to Telegram Channel")
    else: print(f"❌ Telegram Failed: {r.text}")

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

# EXECUTE ALL
post_telegram()
post_devto()
post_hashnode()
# Reddit/Twitter removed if keys not present

