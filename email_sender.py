# email_sender.py
import smtplib
from email.mime.text import MIMEText
from dashboard.auth import get_config

def send_email(to_addr, subject, body, from_addr=None):
    cfg = get_config() or {}
    user = cfg.get("gmail_user")
    app_pass = cfg.get("email_app_password")

    if not user or not app_pass:
        raise RuntimeError("Gmail credentials missing in config.json")

    sender = from_addr or user
    msg = MIMEText(body, "html")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = to_addr

    try:
        smtp = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        smtp.login(user, app_pass)
        smtp.sendmail(sender, [to_addr], msg.as_string())
        smtp.quit()
        return True
    except Exception as e:
        raise RuntimeError("send_email error: " + str(e))
