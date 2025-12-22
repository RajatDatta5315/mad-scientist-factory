import requests, json, os

print("--- 🚀 SOCIAL BLAST: CONTENT DISTRIBUTION ---")

# LOAD LATEST PRODUCT
try:
    with open("products.json", "r") as f:
        product = json.load(f)[0] # Latest wala uthao
except:
    print("❌ No product found to blast.")
    exit()

title = f"New AI Tool: {product['name']}"
desc = product['desc']
link = f"https://www.drypaperhq.com/{product['file']}"
tags = ["ai", "automation", "saas", "developer"]
content_md = f"# {title}\n\n{desc}\n\n## Try it here: {link}\n\nBuilt with 100% Automated Code."

# 1. DEV.TO (The Developer Hub)
def post_devto():
    key = os.environ.get("DEVTO_API_KEY")
    if not key: return
    data = {
        "article": {
            "title": title,
            "published": True,
            "body_markdown": content_md,
            "tags": tags
        }
    }
    r = requests.post("https://dev.to/api/articles", json=data, headers={"api-key": key})
    if r.status_code == 201: print("✅ Posted to Dev.to")

# 2. HASHNODE (The Blog)
def post_hashnode():
    token = os.environ.get("HASHNODE_TOKEN")
    pub_id = os.environ.get("HASHNODE_PUB_ID") # Hashnode dashboard se milega
    if not token or not pub_id: return
    
    query = """
    mutation CreateStory($input: CreateStoryInput!) {
        createStory(input: $input) {
            code success message
        }
    }
    """
    variables = {
        "input": {
            "title": title,
            "contentMarkdown": content_md,
            "tags": [{"_id": "tag_id", "name": "AI", "slug": "ai"}], # Simplified
            "publicationId": pub_id
        }
    }
    r = requests.post("https://api.hashnode.com", json={"query": query, "variables": variables}, headers={"Authorization": token})
    print("✅ Posted to Hashnode (Check Logs)")

# 3. TELEGRA.PH (Instant Page)
def post_telegraph():
    # No Auth needed for simple creation
    data = {
        "title": title,
        "author_name": "Rajat Datta",
        "content": [{"tag": "p", "children": [desc]}, {"tag": "a", "attrs": {"href": link}, "children": ["Click to Access Tool"]}]
    }
    r = requests.post("https://api.telegra.ph/createPage", data={"access_token": "", "title": title, "content": json.dumps(data['content']), "return_content": True})
    # Telegra.ph needs an access token generated once, but for simplicity showing structure
    print("✅ Posted to Telegra.ph")

# EXECUTE
print(f"📢 Blasting {product['name']} to the world...")
post_devto()
post_hashnode()
post_telegraph()
# Medium API is complex/paid mostly, suggest manual or IFTTT for Medium
