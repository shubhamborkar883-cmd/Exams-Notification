import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# Fetch secret tokens securely from GitHub environment variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_alert(message):
    """Sends a formatted notification message directly to your Telegram chat."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ Telegram credentials missing. Skipping broadcast.")
        return

    telegram_url = f"https://telegram.org{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    
    try:
        res = requests.post(telegram_url, json=payload, timeout=10)
        if res.status_code == 200:
            print("🚀 Notification successfully pushed to Telegram!")
        else:
            print(f"❌ Telegram API Error: {res.text}")
    except Exception as e:
        print(f"❌ Failed to connect to Telegram: {e}")

def scrape_all_maharashtra_exams():
    url = "https://mahabharti.in"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
    except Exception as e:
        print(f"❌ Failed to reach portal: {e}")
        return

    soup = BeautifulSoup(response.content, "html.parser")
    job_elements = soup.find_all("a", href=True)
    
    new_alerts = []
    seen_titles = set()
    
    for element in job_elements:
        title_text = element.get_text(strip=True)
        link = element['href']
        
        is_exam_alert = any(keyword in title_text.lower() for keyword in ["bharti", "exam", "mpsc", "पोलीस", "भरती", "निकाल", "जाहीर", "पदांची"])
        
        if is_exam_alert and title_text not in seen_titles and len(title_text) > 15:
            seen_titles.add(title_text)
            new_alerts.append((title_text, link))

    if not new_alerts:
        print("✅ No new exam adjustments detected today.")
        return

    # Check against local file log to only send *brand new* items to Telegram
    log_file = "LIVE_EXAM_ALERTS.md"
    existing_content = ""
    if os.path.exists(log_file):
        with open(log_file, "r", encoding="utf-8") as f:
            existing_content = f.read()

    fresh_entries_markdown = []
    telegram_message_body = ""

    # Process top 5 freshest notifications
    for title, link in new_alerts[:5]:
        markdown_line = f"- **[{datetime.now().strftime('%d-%b-%Y')}]** [{title}]({link})"
        
        # If this alert isn't in our history log yet, it's brand new!
        if title not in existing_content:
            fresh_entries_markdown.append(markdown_line)
            telegram_message_body += f"🔸 *{title}*\n🔗 [Click here to view details]({link})\n\n"

    # Send Broadcast if new alerts exist
    if fresh_entries_markdown:
        # 1. Dispatch Telegram Alert
        alert_header = f"📋 *New Maharashtra Exam Alerts ({datetime.now().strftime('%d-%m-%Y')})*\n\n"
        send_telegram_alert(alert_header + telegram_message_body)

        # 2. Update local Markdown log inside the repository
        header = "# 🚨 Live Maharashtra Government Exams Board\n\n"
        new_content = header + "\n".join(fresh_entries_markdown) + "\n\n" + existing_content.replace(header, "")
        with open(log_file, "w", encoding="utf-8") as f:
            f.write(new_content)
    else:
        print("🔗 All found notices have already been broadcasted previously.")

if __name__ == "__main__":
    scrape_all_maharashtra_exams()
