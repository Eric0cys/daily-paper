import smtplib
import json
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from email.mime.base import MIMEBase
from email import encoders

def send_email_report():
    today = datetime.now().strftime("%Y-%m-%d")
    
    # 读取精读数据
    with open(f"data/{today}_enhanced.json", "r", encoding="utf-8") as f:
        papers = json.load(f)
    
    # 构建 HTML 邮件正文
    html_content = f"""
    <html>
    <head><title>Daily arXiv Papers - {today}</title></head>
    <body>
    <h2>📚 Daily arXiv Papers Digest - {today}</h2>
    """
    for paper in papers:
        html_content += f"""
        <div style="margin-bottom: 30px; border-bottom: 1px solid #ccc;">
            <h3><a href="{paper['pdf_url']}">{paper['title']}</a></h3>
            <p><b>Authors:</b> {', '.join(paper['authors'])}</p>
            <p><b>Published:</b> {paper['published']}</p>
            <div style="background-color: #f0f0f0; padding: 10px;">
                <pre>{paper['ai_summary']}</pre>
            </div>
        </div>
        """
    html_content += "</body></html>"
    
    # SMTP 发送
    sender = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASS")
    receiver = os.getenv("EMAIL_TO")
    
    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = receiver
    msg["Subject"] = f"📖 Daily arXiv Papers Digest - {today}"
    msg.attach(MIMEText(html_content, "html"))
    
    # 可选：添加附件
    filename = f"data/{today}_enhanced.json"
    with open(filename, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {today}_paper_summaries.json",
        )
        msg.attach(part)
    
    # 发送邮件
    with smtplib.SMTP_SSL("smtp.qq.com", 465) as server:
        server.login(sender, password)
        server.sendmail(sender, receiver, msg.as_string())
    
    print(f"Email sent to {receiver}")

if __name__ == "__main__":
    send_email_report()
