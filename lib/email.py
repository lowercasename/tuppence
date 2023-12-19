import os
import requests
from dotenv import load_dotenv
from flask import render_template
from models.user import User

load_dotenv()

class EmailException(Exception):
    pass

def send_email(to, subject, body):
    mailgun_api_key = os.getenv('MAILGUN_API_KEY')
    mailgun_domain = os.getenv('MAILGUN_DOMAIN')
    
    if not mailgun_api_key or not mailgun_domain:
        raise EmailException("Mailgun credentials not set")

    response = requests.post(
        f"https://api.mailgun.net/v3/{mailgun_domain}/messages",
        auth=("api", mailgun_api_key),
        data={"from": f"Tuppence <mail@{mailgun_domain}>",
                "to": to,
                "subject": subject,
                "html": body})
    if response.status_code != 200:
        raise EmailException(f"Error sending email: {response.text}")

def send_verify_email(user: User):
    link = f"https://{os.getenv('DOMAIN')}/auth/{user.login_token}"
    html = render_template('email/verify_email.html', link=link)
    send_email(
        user.email_address,
        "Verify your email address",
        html)

def send_login_email(user: User):
    link = f"https://{os.getenv('DOMAIN')}/auth/{user.login_token}"
    html = render_template('email/login.html', link=link)
    send_email(
        user.email_address,
        "Login to Tuppence",
        html)