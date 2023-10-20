import smtplib
from email.mime.text import MIMEText
import datetime
import os
import json
from dotenv import load_dotenv


# Load the environment variables from the .env file
load_dotenv()

# Access the variables from the .env file
email_sender = os.getenv("EMAIL_SENDER")
email_recipients = json.loads(os.getenv("EMAIL_RECIPIENTS"))
email_password = os.getenv("EMAIL_PASSWORD")

def send_email(subject, body):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = email_sender
    msg["To"] = ", ".join(email_recipients)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp_server:
        smtp_server.login(email_sender, email_password)
        smtp_server.sendmail(email_sender, email_recipients, msg.as_string())

    print(f"{datetime.datetime.now()} Message sent!")
