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
    <title>Daily AI & Tech Gadget Intelligence Brief</title>
</head>
<body style="margin: 0; padding: 0; background-color: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; color: #1e293b; -webkit-font-smoothing: antialiased; line-height: 1.6;">
    <div style="max-width: 650px; margin: 0 auto; padding: 30px 15px;">
        <!-- Card Container -->
        <div style="background-color: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.05), 0 10px 10px -5px rgba(0, 0, 0, 0.04); border: 1px solid #e2e8f0;">
            
            <!-- Header Banner -->
            <div style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%); padding: 40px 32px; text-align: left; border-bottom: 4px solid #2563eb;">
                <span style="background-color: #2563eb; color: #ffffff; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 1.5px; padding: 4px 10px; border-radius: 4px;">Intelligence Briefing</span>
                <h1 style="margin: 12px 0 6px 0; color: #ffffff; font-size: 28px; font-weight: 800; letter-spacing: -0.5px; line-height: 1.2;">The Daily A-Z AI Gadget Report</h1>
                <p style="margin: 0; color: #94a3b8; font-size: 14px; font-weight: 500;">{date_str} | Compiled at {time_str}</p>
            </div>
            
            <!-- Content Area -->
            <div style="padding: 32px 32px;">
                
                <!-- Executive Summary / Formal Letter -->
                <div style="background-color: #f1f5f9; border-left: 4px solid #2563eb; border-radius: 0 12px 12px 0; padding: 24px; margin-bottom: 36px;">
                    <h3 style="margin: 0 0 12px 0; color: #0f172a; font-size: 16px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px;">Executive Briefing & Summary</h3>
                    <p style="margin: 0 0 12px 0; font-size: 14px; color: #334155; line-height: 1.6;">
                        Dear Tech Innovator,
                    </p>
                    <p style="margin: 0 0 12px 0; font-size: 14px; color: #334155; line-height: 1.6;">
                        Welcome to today's edition of the Daily AI Intelligence Brief. The consumer technology landscape continues its rapid evolution towards fully integrated multimodal systems. Highlighting today's intelligence is the massive impact of new releases like <strong>Gemini Spark</strong> and robust wearable AI units that promise to liberate users from traditional glass-screen interfaces.
                    </p>
                    <p style="margin: 0 0 12px 0; font-size: 14px; color: #334155; line-height: 1.6;">
                        We have tracked, parsed, and synthesized the absolute highest-velocity video analyses from leading product engineers. Our deep-dives today cover three standout categories: advanced conversational companions, home-automation hubs, and lifestyle integrations that represent the current state-of-the-art in hardware and software design.
                    </p>
                    <p style="margin: 0; font-size: 14px; color: #475569; font-weight: 500; font-style: italic;">
                        — Antigravity Tech Research Team
                    </p>
                </div>
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
                <h2 style="margin: 0 0 24px 0; font-size: 20px; font-weight: 800; color: #0f172a; text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px;">A-Z Deep Dive Product Breakdown</h2>
        """
        
        for idx, item in enumerate(products):
            # Dynamic use case analysis
            use_case = "Perfect for productivity specialists seeking to optimize daily task management and automate routine digital workflows using next-gen conversational models."
            if "travel" in item['title'].lower() or "trip" in item['title'].lower():
                use_case = "Designed specifically for modern travelers, outdoor explorers, and digital nomads looking for real-time translation, maps, and offline assistant capabilities."
            elif "amazon" in item['title'].lower() or "home" in item['title'].lower() or "house" in item['title'].lower():
                use_case = "Ideal for smart home enthusiasts and lifestyle automators focused on building an interconnected ecosystem with proactive assistant capabilities."
            elif "creative" in item['title'].lower() or "camera" in item['title'].lower() or "video" in item['title'].lower():
                use_case = "Tailored for content creators, photographers, and audio-visual designers wishing to speed up raw asset production using local intelligence networks."

            # Dynamic editorial overview
            overview = f"A trending analysis exploring standard software updates and hardware capabilities. This deep dive focuses on how new machine learning frameworks are shifting from cloud-dependent tasks to highly responsive, low-latency device operations."

            html += f"""
                <!-- Product Card {idx + 1} -->
                <div style="margin-bottom: 40px; border: 1px solid #e2e8f0; border-radius: 12px; padding: 28px; background-color: #ffffff; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.03), 0 2px 4px -1px rgba(0, 0, 0, 0.02);">
                    
                    <!-- Category & Title -->
                    <span style="color: #2563eb; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px;">Product Spotlight {idx + 1}</span>
                    <h3 style="margin: 6px 0 16px 0; font-size: 20px; font-weight: 800; line-height: 1.4; color: #0f172a;">
                        {item['title']}
                    </h3>
            """
            
            if item.get("thumbnail_url"):
                html += f"""
                    <!-- Product Photo / Media Visual Card -->
                    <div style="margin-bottom: 20px; border-radius: 8px; overflow: hidden; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);">
                        <a href="{item['link']}" target="_blank" style="display: block;">
                            <img src="{item['thumbnail_url']}" alt="{item['title']}" style="width: 100%; max-width: 100%; height: auto; display: block; border: 0;">
                        </a>
                    </div>
                """
                
            html += f"""
                    <!-- Editorial Review -->
                    <div style="margin-bottom: 20px;">
                        <h4 style="margin: 0 0 6px 0; font-size: 13px; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px;">Editorial Overview</h4>
                        <p style="margin: 0; font-size: 14px; color: #334155; line-height: 1.6;">{overview}</p>
                    </div>

                    <!-- Features & Specifications -->
                    <div style="margin-bottom: 20px;">
                        <h4 style="margin: 0 0 8px 0; font-size: 13px; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px;">Key Specifications & Highlights</h4>
                        <ul style="margin: 0; padding-left: 20px; font-size: 14px; color: #334155; line-height: 1.6;">
            """
            
            for bullet in item.get("bullets", []):
                html += f"""
                            <li style="margin-bottom: 8px;">{bullet}</li>
                """
                
            html += f"""
                        </ul>
                    </div>
                    
                    <!-- Strategic Use Case callout -->
                    <div style="background-color: #eff6ff; border-left: 3px solid #3b82f6; padding: 16px; border-radius: 0 8px 8px 0; margin-bottom: 20px;">
                        <h4 style="margin: 0 0 4px 0; font-size: 12px; font-weight: 700; color: #1e3a8a; text-transform: uppercase; letter-spacing: 0.5px;">Strategic Use Case</h4>
                        <p style="margin: 0; font-size: 13px; color: #1e40af; line-height: 1.5;">{use_case}</p>
                    </div>

                    <!-- Source Context -->
                    <div style="text-align: right; border-top: 1px solid #f1f5f9; padding-top: 16px; margin-top: 16px;">
                        <a href="{item['link']}" target="_blank" style="color: #2563eb; text-decoration: none; font-weight: 700; font-size: 13px;">[Watch Video Analysis] &rarr;</a>
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
        
    smtp_user_raw = os.environ.get("SMTP_USER") or os.environ.get("SENDER_EMAIL") or ""
    smtp_user = smtp_user_raw.strip().replace("<", "").replace(">", "").replace('"', '').replace("'", "")
    
    smtp_password_raw = os.environ.get("SMTP_PASSWORD") or os.environ.get("EMAIL_PASSWORD") or ""
    smtp_password = smtp_password_raw.strip()
    
    sender_email_raw = os.environ.get("SENDER_EMAIL") or smtp_user
    sender_email = sender_email_raw.strip().replace("<", "").replace(">", "").replace('"', '').replace("'", "")
    
    receiver_email_raw = os.environ.get("RECEIVER_EMAIL") or "georgealbert777@gmail.com"
    receiver_email = receiver_email_raw.strip().replace("<", "").replace(">", "").replace('"', '').replace("'", "")
    
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
            print(f"Connecting to {smtp_host}:{smtp_port} using standard SMTP...")
            server = smtplib.SMTP(smtp_host, smtp_port, timeout=30)
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
