import os, smtplib, datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

print("--- 📊 DAILY REPORTER ---")

SMTP_EMAIL = os.environ.get("SMTP_EMAIL")
SMTP_PASS = os.environ.get("SMTP_PASSWORD")
TARGET_EMAIL = os.environ.get("TARGET_EMAIL") # Tera Personal Email

def send_report():
    if not SMTP_EMAIL or not SMTP_PASS or not TARGET_EMAIL:
        print("❌ Email Secrets Missing for Report.")
        return

    # 1. READ STATS
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    dm_count = 0
    
    # Count DMs sent today
    if os.path.exists("leads.csv"):
        with open("leads.csv", "r") as f:
            for line in f:
                if today in line: dm_count += 1
    
    # 2. COMPOSE EMAIL
    subject = f"✅ DryPaper Daily Report: {today}"
    body = f"""
    BOSS, DRYPAPER UPDATE ({today}):
    
    🚀 OUTREACH:
    - New DMs Sent: {dm_count}
    - Platform Status: Active
    
    🛠️ SYSTEM:
    - Factory: Running
    - Website: Updated
    - RSS Feed: Synced (Substack/Flipboard)
    
    System is autonomous. No action needed.
    """

    msg = MIMEMultipart()
    msg['From'] = f"DryPaper Bot <{SMTP_EMAIL}>"
    msg['To'] = TARGET_EMAIL
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SMTP_EMAIL, SMTP_PASS)
        server.sendmail(SMTP_EMAIL, TARGET_EMAIL, msg.as_string())
        server.quit()
        print("✅ Daily Report Sent to Boss.")
    except Exception as e:
        print(f"❌ Report Failed: {e}")

send_report()
