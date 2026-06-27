import smtplib
import os
from email.mime.text import MIMEText
from dotenv import load_dotenv
from email.utils import formataddr

load_dotenv(".env")

sender_email = os.getenv('SENDER_EMAIL')
sender_password = os.getenv('SENDER_PASSWORD')
recipient_email = os.getenv('RECIPIENT_EMAIL')


if not sender_email or not sender_password or not recipient_email:
    raise ValueError("Set SENDER_EMAIL, SENDER_PASSWORD, and RECIPIENT_EMAIL in .env")

msg = MIMEText("This is a test email from yfinance alerts.")
msg['Subject'] = "YFinance Alert"
msg['From'] = formataddr(("YFinance Alerts", sender_email))
msg['To'] = recipient_email

with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
    server.login(sender_email, sender_password)
    server.sendmail(sender_email, recipient_email, msg.as_string())

print("Email sent successfully!")
