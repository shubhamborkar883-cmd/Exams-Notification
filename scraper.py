import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def scrape_all_maharashtra_exams():
    # Targeted live aggregator URL tracking all Maha state exams (MPSC, ZP, Police, etc.)
    url = "https://mahabharti.in/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    print(f"🔄 Scanning all Maharashtra Exam portals on {datetime.now().strftime('%d-%m-%Y')}...")
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
    except Exception as e:
        print(f"❌ Failed to reach portal: {e}")
        return

    soup = BeautifulSoup(response.content, "html.parser")
    
    # Extracting listed updates from the main alert grid container
    job_elements = soup.find_all("a", href=True)
    
    new_alerts = []
    seen_titles = set()
    
    for element in job_elements:
        title_text = element.get_text(strip=True)
        link = element['href']
        
        # Filtering for entries containing key recruitment triggers or Marathi status flags
        is_exam_alert = any(keyword in title_text.lower() for keyword in ["bharti", "exam", "mpsc", "पोलीस", "भरती", "निकाल", "जाहीर", "पदांची"])
        
        if is_exam_alert and title_text not in seen_titles and len(title_text) > 15:
            seen_titles.add(title_text)
            new_alerts.append(f"- **[{datetime.now().strftime('%d-%b-%Y')}]** [{title_text}]({link})")

    if not new_alerts:
        print("✅ No new exam adjustments detected today.")
        return

    # Keep only the top 10 fresh alerts
    latest_updates = new_alerts[:10]
    
    # Save the tracked updates directly into a Markdown file within the GitHub environment
    log_file = "LIVE_EXAM_ALERTS.md"
    
    # Read existing content if file exists
    existing_content = ""
    if os.path.exists(log_file):
        with open(log_file, "r", encoding="utf-8") as f:
            existing_content = f.read()

    # Construct clean updated log file
    header = "# 🚨 Live Maharashtra Government Exams Board\n*Automatically updated via GitHub Actions workflow.*\n\n"
    
    # Filter out updates already written to avoid repetitive logging
    fresh_entries = [entry for entry in latest_updates if entry not in existing_content]
    
    if fresh_entries:
        new_content = header + "\n".join(fresh_entries) + "\n\n" + existing_content.replace(header, "")
        with open(log_file, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"📝 successfully logged {len(fresh_entries)} new state exam updates to {log_file}!")
    else:
        print("🔗 Verified: All scraped notices are already captured.")

if __name__ == "__main__":
    scrape_all_maharashtra_exams()
