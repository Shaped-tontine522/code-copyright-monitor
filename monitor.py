
import os
import requests
from datetime import datetime
import smtplib
from email.mime.text import MIMEText

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
SEARCH_QUERY = "your_unique_code_signature_here"
LOG_FILE = "logs/report.log"

SLACK_WEBHOOK = os.getenv("SLACK_WEBHOOK")  # optional
EMAIL_TO = os.getenv("EMAIL_TO")            # optional
EMAIL_FROM = os.getenv("EMAIL_FROM")        # optional
SMTP_SERVER = os.getenv("SMTP_SERVER")      # optional

headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

def search_similar_code():
    url = f"https://api.github.com/search/code?q={SEARCH_QUERY}"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        return []
    return response.json().get("items", [])

def notify_slack(text):
    if not SLACK_WEBHOOK:
        return
    try:
        requests.post(SLACK_WEBHOOK, json={"text": text})
    except Exception:
        pass

def notify_email(text):
    if not (EMAIL_TO and EMAIL_FROM and SMTP_SERVER):
        return
    try:
        msg = MIMEText(text)
        msg["Subject"] = "⚠️ Code Copy Alert"
        msg["From"] = EMAIL_FROM
        msg["To"] = EMAIL_TO
        with smtplib.SMTP(SMTP_SERVER) as s:
            s.send_message(msg)
    except Exception:
        pass

def log_results(results):
    os.makedirs("logs", exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(f"\n\n=== Scan at {datetime.now()} ===\n")
        if not results:
            f.write("✅ No similar code detected\n")
        else:
            f.write("⚠️ Similar code found:\n")
            for item in results:
                f.write(f"{item['repository']['html_url']}\n")

def main():
    results = search_similar_code()
    log_results(results)
    if results:
        msg = "⚠️ Potential code copy found!"
        print(msg)
        notify_slack(msg)
        notify_email(msg)
    else:
        print("✅ Clean — No match found")

if __name__ == "__main__":
    main()

