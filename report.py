import os
import requests
import re
import json
from bs4 import BeautifulSoup
from datetime import datetime

# Simple pure-python .env loader for environment isolation (used for local testing)
def load_dotenv(dotenv_path=".env"):
    if os.path.exists(dotenv_path):
        with open(dotenv_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, val = line.split("=", 1)
                    key = key.strip()
                    val = val.strip().strip('"').strip("'")
                    os.environ[key] = val

# Load configuration from .env file (if present)
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

def extract_features(video):
    runs_text = []
    
    # Try detailedMetadataSnippets
    snippets = video.get("detailedMetadataSnippets", [])
    for snippet in snippets:
        runs = snippet.get("snippetText", {}).get("runs", [])
        text = "".join([r.get("text", "") for r in runs]).strip()
        if text:
            runs_text.append(text)
            
    # Fallback to descriptionSnippet
    if not runs_text:
        desc_snippet = video.get("descriptionSnippet", {})
        runs = desc_snippet.get("runs", [])
        text = "".join([r.get("text", "") for r in runs]).strip()
        if text:
            runs_text.append(text)
            
    full_text = " ".join(runs_text) if runs_text else ""
    
    # Extract clean sentence bullet points
    sentences = re.split(r'\. |\n|; ', full_text)
    bullets = []
    for s in sentences:
        s_clean = s.strip().strip('.').strip('-').strip('*').strip()
        # Filter out timelines (e.g. 00:00) or short items
        if len(s_clean) > 15 and not re.match(r'^\d{2}:\d{2}', s_clean):
            bullets.append(s_clean)
            
    if not bullets:
        bullets = [
            "Detailed features and specs breakdowns are available in the linked video.",
            "Includes hands-on demonstrations and reviews of the trending product."
        ]
        
    return bullets[:4]

def generate_html_report(products, run_time):
    date_str = run_time.strftime('%B %d, %Y')
    time_str = run_time.strftime('%I:%M %p')
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Daily AI Gadgets Report</title>
</head>
<body style="margin: 0; padding: 0; background-color: #f1f5f9; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; -webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale; color: #334155;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px 10px;">
        <!-- Card Container -->
        <div style="background-color: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1); border: 1px solid #e2e8f0;">
            
            <!-- Header Banner -->
            <div style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); padding: 32px 24px; text-align: center; border-bottom: 4px solid #3b82f6;">
                <h1 style="margin: 0; color: #ffffff; font-size: 26px; font-weight: 800; letter-spacing: -0.5px; line-height: 1.2;">Daily AI Gadgets Report</h1>
                <p style="margin: 8px 0 0 0; color: #94a3b8; font-size: 14px; font-weight: 500;">{date_str} at {time_str}</p>
            </div>
            
            <!-- Content Area -->
            <div style="padding: 28px 24px;">
    """
    
    if not products:
        html += """
                <div style="text-align: center; padding: 20px 0;">
                    <div style="background-color: #fef3c7; border: 1px solid #f59e0b; border-radius: 12px; padding: 16px; margin-bottom: 24px; text-align: left;">
                        <h3 style="margin: 0 0 8px 0; color: #b45309; font-size: 16px; font-weight: 700;">Notice</h3>
                        <p style="margin: 0; color: #78350f; font-size: 14px; line-height: 1.5;">We encountered a temporary scraping issue when checking YouTube today. The page layout may have changed, or the request was throttled.</p>
                    </div>
                    <p style="font-size: 16px; line-height: 1.5; color: #475569;">You can browse the latest trending AI products directly on YouTube:</p>
                    <a href="https://www.youtube.com/results?search_query=latest+ai+gadgets+features" target="_blank" style="display: inline-block; background-color: #3b82f6; color: #ffffff; padding: 12px 24px; border-radius: 8px; text-decoration: none; font-weight: 600; font-size: 14px; margin-top: 8px; box-shadow: 0 4px 6px -1px rgba(59, 130, 246, 0.3);">Search AI Gadgets on YouTube</a>
                </div>
        """
    else:
        html += """
                <h2 style="margin: 0 0 20px 0; font-size: 18px; font-weight: 700; color: #0f172a; text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 2px solid #f1f5f9; padding-bottom: 8px;">Top Trending Products & Features</h2>
        """
        
        for idx, item in enumerate(products):
            html += f"""
                <!-- Product Card {idx + 1} -->
                <div style="margin-bottom: 28px; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px; background-color: #f8fafc; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);">
                    <!-- Video Title -->
                    <h3 style="margin: 0 0 12px 0; font-size: 18px; font-weight: 700; line-height: 1.4;">
                        <a href="{item['link']}" target="_blank" style="color: #2563eb; text-decoration: none;">{item['title']}</a>
                    </h3>
            """
            
            if item.get("thumbnail_url"):
                html += f"""
                    <!-- Product Photo -->
                    <div style="margin-bottom: 16px; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); border: 1px solid #e2e8f0;">
                        <a href="{item['link']}" target="_blank">
                            <img src="{item['thumbnail_url']}" alt="{item['title']}" style="width: 100%; max-width: 100%; height: auto; display: block; border: 0;">
                        </a>
                    </div>
                """
                
            html += """
                    <!-- Features List -->
                    <div style="margin-top: 12px;">
                        <h4 style="margin: 0 0 8px 0; font-size: 13px; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px;">A-Z Feature Highlights:</h4>
                        <ul style="margin: 0; padding-left: 20px; font-size: 14px; color: #475569; line-height: 1.6;">
            """
            
            for bullet in item.get("bullets", []):
                html += f"""
                            <li style="margin-bottom: 6px;">{bullet}</li>
                """
                
            html += f"""
                        </ul>
                    </div>
                    
                    <!-- Direct Link Button -->
                    <div style="margin-top: 16px; text-align: right;">
                        <a href="{item['link']}" target="_blank" style="display: inline-block; background-color: #f1f5f9; color: #334155; padding: 6px 14px; border-radius: 6px; text-decoration: none; font-weight: 600; font-size: 12px; border: 1px solid #cbd5e1;">Watch Feature Breakdown &rarr;</a>
                    </div>
                </div>
            """
            
    html += f"""
            </div>
            
            <!-- Footer -->
            <div style="background-color: #f8fafc; padding: 20px 24px; border-top: 1px solid #e2e8f0; text-align: center;">
                <p style="margin: 0; font-size: 12px; color: #94a3b8; line-height: 1.5;">This is an automated report compiled from YouTube search results for latest AI gadgets.</p>
                <p style="margin: 4px 0 0 0; font-size: 11px; color: #cbd5e1;">Recipient: georgealbert777@gmail.com</p>
            </div>
        </div>
    </div>
</body>
</html>
    """
    return html

def send_email(subject, html_content):
    # Robustly load SMTP host/server, defaulting to smtp.gmail.com if empty or not set
    smtp_host_raw = os.environ.get("SMTP_HOST") or os.environ.get("SMTP_SERVER") or ""
    smtp_host = smtp_host_raw.strip() if smtp_host_raw.strip() else "smtp.gmail.com"
    
    # Safely parse port, handling empty strings and non-integer inputs gracefully
    smtp_port_raw = os.environ.get("SMTP_PORT", "587")
    try:
        smtp_port = int(smtp_port_raw) if smtp_port_raw.strip() else 587
    except ValueError:
        smtp_port = 587
        
    smtp_user = os.environ.get("SMTP_USER") or os.environ.get("SENDER_EMAIL") or ""
    smtp_password = os.environ.get("SMTP_PASSWORD") or os.environ.get("EMAIL_PASSWORD") or ""
    sender_email = os.environ.get("SENDER_EMAIL") or smtp_user
    receiver_email = os.environ.get("RECEIVER_EMAIL", "georgealbert777@gmail.com")
    
    if not smtp_user or not smtp_password:
        print("\n[Warning] SMTP credentials not set. Saving report as local file for manual verification.")
        local_path = os.path.join(os.path.dirname(__file__), "local_report.html")
        with open(local_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"HTML Report generated and saved locally to: {os.path.abspath(local_path)}")
        return
        
    try:
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = sender_email
        msg["To"] = receiver_email
        
        part = MIMEText(html_content, "html", "utf-8")
        msg.attach(part)
        
        import smtplib
        print(f"SMTP Config - Host: {smtp_host}, Port: {smtp_port}, User: {smtp_user}")
        
        if smtp_port == 465:
            print("Initializing SMTP_SSL connection...")
            server = smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=30)
        else:
            print("Initializing standard SMTP connection...")
            server = smtplib.SMTP()
            print(f"Connecting to {smtp_host}:{smtp_port}...")
            server.connect(smtp_host, smtp_port)
            print("Sending EHLO...")
            server.ehlo()
            print("Starting TLS (starttls)...")
            server.starttls()
            print("Sending EHLO post-TLS...")
            server.ehlo()
            
        print("Attempting login...")
        server.login(smtp_user, smtp_password)
        print("Sending mail...")
        server.sendmail(sender_email, receiver_email, msg.as_string())
        print("Closing SMTP connection...")
        server.quit()
        print("Daily report email successfully sent.")
        print(f"Daily report email successfully sent to {receiver_email}.")
    except Exception as e:
        print(f"Error during email automation: {e}")

def get_ai_gadget_report():
    run_time = datetime.now()
    print(f"--- {run_time.strftime('%Y-%m-%d %H:%M')} — DAILY REPORT RUN ---")
    
    url = "https://www.youtube.com/results?search_query=latest+ai+gadgets+features"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    
    products = []
    
    try:
        response = requests.get(url, headers=headers)
        html = response.text
        
        # Try parsing via ytInitialData first (modern YouTube page layout)
        pattern = r"ytInitialData\s*=\s*({.*?});"
        match = re.search(pattern, html)
        if match:
            try:
                data = json.loads(match.group(1))
                videos = []
                def recurse(node):
                    if isinstance(node, dict):
                        if "videoRenderer" in node:
                            videos.append(node["videoRenderer"])
                        else:
                            for k, v in node.items():
                                recurse(v)
                    elif isinstance(node, list):
                        for item in node:
                            recurse(item)
                recurse(data)
                
                for video in videos:
                    video_id = video.get("videoId")
                    if not video_id:
                        continue
                    
                    title_text = ""
                    if "title" in video and "runs" in video["title"] and len(video["title"]["runs"]) > 0:
                        title_text = video["title"]["runs"][0].get("text", "")
                    elif "title" in video and "simpleText" in video["title"]:
                        title_text = video["title"]["simpleText"]
                    
                    # Highest resolution thumbnail
                    thumbnails = video.get("thumbnail", {}).get("thumbnails", [])
                    thumbnail_url = ""
                    if thumbnails:
                        sorted_thumbnails = sorted(thumbnails, key=lambda x: x.get("width", 0), reverse=True)
                        thumbnail_url = sorted_thumbnails[0].get("url", "")
                        
                    bullets = extract_features(video)
                    
                    if title_text:
                        products.append({
                            "title": title_text,
                            "link": f"https://www.youtube.com/watch?v={video_id}",
                            "thumbnail_url": thumbnail_url,
                            "bullets": bullets
                        })
                        
                        if len(products) >= 3:
                            break
            except Exception as parse_err:
                print(f"JSON Parsing Error (attempting fallback): {parse_err}")
                
        # Fallback to BeautifulSoup if ytInitialData is not found or failed to return products
        if not products:
            try:
                soup = BeautifulSoup(html, 'html.parser')
                results = soup.find_all('a', href=True)
                for result in results:
                    title = result.get('title')
                    link = result.get('href')
                    
                    if title and '/watch' in link:
                        watch_part = link.split('/watch')[-1]
                        full_link = f"https://www.youtube.com/watch{watch_part}"
                        
                        products.append({
                            "title": title,
                            "link": full_link,
                            "thumbnail_url": "",
                            "bullets": [
                                "Detailed features and specs breakdowns are available in the linked video.",
                                "Includes hands-on demonstrations and reviews of the trending product."
                            ]
                        })
                        
                        if len(products) >= 3:
                            break
            except Exception as soup_err:
                print(f"BeautifulSoup Parsing Error: {soup_err}")
                
    except Exception as e:
        print(f"Network Scraper Error: {e}")
        
    # Generate HTML & Send Email
    subject = f"Daily AI Gadgets Report — {run_time.strftime('%Y-%m-%d')}"
    try:
        html_report = generate_html_report(products, run_time)
        send_email(subject, html_report)
    except Exception as email_err:
        print(f"Critical Failure compiling/sending report: {email_err}")

if __name__ == "__main__":
    get_ai_gadget_report()
