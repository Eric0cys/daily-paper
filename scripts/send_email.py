import smtplib
import json
import os
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from email.mime.base import MIMEBase
from email import encoders

def send_email_report():
    today = datetime.now().strftime("%Y-%m-%d")
    data_file = f"data/{today}_enhanced.json"
    
    # 1. 检查文件是否存在
    if not os.path.exists(data_file):
        print(f"错误：文件 {data_file} 不存在，请先运行 fetch 和 summarize 脚本")
        sys.exit(1)
    
    # 2. 读取精读数据，处理空列表情况
    with open(data_file, "r", encoding="utf-8") as f:
        papers = json.load(f)
    
    if not papers:
        print("警告：没有论文数据，将发送空报告")
    
    # 3. 构建 HTML 邮件正文（增加对空数据的处理）
    html_content = f"""
    <html>
    <head><title>Daily arXiv Papers - {today}</title></head>
    <body>
    <h2>📚 Daily arXiv Papers Digest - {today}</h2>
    """
    if not papers:
        html_content += "<p>今日没有找到新的相关论文。</p>"
    else:
        for paper in papers:
            # 防止某些字段缺失导致 KeyError
            title = paper.get('title', 'No Title')
            pdf_url = paper.get('pdf_url', '#')
            authors = paper.get('authors', ['Unknown'])
            published = paper.get('published', 'Unknown date')
            ai_summary = paper.get('ai_summary', 'AI 摘要生成失败')
            
            html_content += f"""
            <div style="margin-bottom: 30px; border-bottom: 1px solid #ccc;">
                <h3><a href="{pdf_url}">{title}</a></h3>
                <p><b>Authors:</b> {', '.join(authors)}</p>
                <p><b>Published:</b> {published}</p>
                <div style="background-color: #f0f0f0; padding: 10px;">
                    <pre style="white-space: pre-wrap; word-wrap: break-word;">{ai_summary}</pre>
                </div>
            </div>
            """
    html_content += "</body></html>"
    
    # 4. 从环境变量读取邮箱配置（与 GitHub Secrets 名称保持一致）
    sender = os.getenv("MAIL_USER")      # 你的 QQ 邮箱地址
    password = os.getenv("MAIL_PASSWORD")    # QQ 邮箱授权码（16位）
    receiver = os.getenv("MAIL_TO")      # 收件人邮箱
    
    # 检查必需的环境变量
    if not all([sender, password, receiver]):
        print("错误：请设置环境变量 EMAIL_USER, EMAIL_PASS, EMAIL_TO")
        sys.exit(1)
    
    # 5. 构建邮件
    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = receiver
    msg["Subject"] = f"📖 Daily arXiv Papers Digest - {today}"
    msg.attach(MIMEText(html_content, "html"))
    
    # 6. 添加附件（文件必须存在）
    if os.path.exists(data_file):
        with open(data_file, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename={today}_paper_summaries.json"
            )
            msg.attach(part)
    else:
        print(f"附件 {data_file} 不存在，跳过附件添加")
    
    # 7. 发送邮件（QQ邮箱使用 SSL）
    try:
        # QQ 邮箱 SMTP 服务器：smtp.qq.com，端口 465（SSL）
        with smtplib.SMTP_SSL("smtp.qq.com", 465) as server:
            server.login(sender, password)
            server.sendmail(sender, receiver, msg.as_string())
        print(f"邮件发送成功！收件人: {receiver}")
    except Exception as e:
        print(f"邮件发送失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    send_email_report()
