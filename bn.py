import requests
import time
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

# API URL
api_url = "https://www.binance.com/bapi/composite/v1/public/cms/article/list/query?type=1&catalogId=48&pageNo=1&pageSize=20"

# Email configuration
SMTP_SERVER = 'smtp-relay.brevo.com'  # 替换为你的SMTP服务器
SMTP_PORT = 587  # 常用的TLS端口
EMAIL_ADDRESS = ''  # 替换为你的邮箱地址
EMAIL_PASSWORD = ''  # 替换为你的邮箱密码
RECIPIENT_EMAIL = ''  # 替换为收件人邮箱地址

# 记录已处理的文章ID以避免重复
processed_article_ids = set()

# 监控间隔（秒）
monitor_interval = 3  # 每3秒检查一次

# 打印带有时间戳的消息
def log_with_time(message):
    """打印带有时间戳的消息。"""
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{current_time}] {message}")

# 初始化，获取现有文章ID
def initialize_processed_articles():
    """初始化，通过获取当前文章ID来避免对现有文章发送警报。"""
    try:
        response = requests.get(api_url)
        data = response.json()

        if data["code"] == "000000" and data["data"]:
            articles = data["data"]["catalogs"][0]["articles"]

            for article in articles:
                article_id = article["id"]
                processed_article_ids.add(article_id)

        log_with_time("初始化完成。正在监控新文章...")
    
    except Exception as e:
        log_with_time(f"初始化时出错: {e}")

# 发送电子邮件通知
def send_email(subject, body):
    """发送电子邮件通知。"""
    try:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = RECIPIENT_EMAIL

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # 将连接升级为安全的加密SSL/TLS连接
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, RECIPIENT_EMAIL, msg.as_string())

        # 记录发送邮件的时间
        send_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_with_time(f"邮件已发送: {subject}，发送时间: {send_time}")
    
    except Exception as e:
        log_with_time(f"发送邮件时出错: {e}")

# 检查新文章
def check_for_new_articles():
    """检查API中的新文章。"""
    try:
        response = requests.get(api_url)
        data = response.json()

        if data["code"] == "000000" and data["data"]:
            articles = data["data"]["catalogs"][0]["articles"]

            for article in articles:
                article_id = article["id"]
                title = article["title"]
                release_date = datetime.fromtimestamp(article["releaseDate"] / 1000).strftime('%Y-%m-%d %H:%M:%S')

                # 检查文章ID是否为新文章
                if article_id not in processed_article_ids:
                    log_with_time(f"发现新文章: {title}")
                    email_body = f"新文章已找到:\n\n标题: {title}\n发布日期: {release_date}"
                    send_email("上bi提醒", email_body)

                    # 记录已处理的文章ID
                    processed_article_ids.add(article_id)

    except Exception as e:
        log_with_time(f"获取或处理数据时出错: {e}")

# 持续监控
def monitor():
    """启动监控程序。"""
    initialize_processed_articles()

    while True:
        check_for_new_articles()
        time.sleep(monitor_interval)

if __name__ == "__main__":
    monitor()
