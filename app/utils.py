import hashlib
import smtplib
import socket
from email.mime.text import MIMEText
from app.config import settings

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return hash_password(plain_password) == hashed_password

def send_email(to_email: str, otp: str):
    msg = MIMEText(f"Your verification code is: {otp}\n\nThis code expires in 2 minutes.")
    msg["Subject"] = "Your OTP Code"
    msg["From"] = settings.smtp_from
    msg["To"] = to_email
    
    socket.setdefaulttimeout(30)
    
    if settings.smtp_port == 2525:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            server.login(settings.smtp_user, settings.smtp_pass)
            server.sendmail(settings.smtp_from, to_email, msg.as_string())
    else:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(settings.smtp_user, settings.smtp_pass)
            server.sendmail(settings.smtp_from, to_email, msg.as_string())