import smtplib
import threading
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from datetime import datetime


def send_email_alert(screenshot_path=None):
    sender   = os.environ.get("ALERT_EMAIL_SENDER")
    password = os.environ.get("ALERT_EMAIL_PASSWORD")
    receiver = os.environ.get("ALERT_EMAIL_RECEIVER")

    if not all([sender, password, receiver]):
        print("[EMAIL] Skipped — env variables not set.")
        return

    msg = MIMEMultipart()
    msg['Subject'] = "AI Driver Safety Alert — Drowsiness Detected"
    msg['From']    = sender
    msg['To']      = receiver

    body = MIMEText(
        f"Drowsiness detected at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.\n"
        "Please check on the driver immediately.\n\n"
        "— AI Driver Safety System",
        'plain'
    )
    msg.attach(body)

    if screenshot_path and os.path.exists(screenshot_path):
        with open(screenshot_path, 'rb') as f:
            img = MIMEImage(f.read(), name=os.path.basename(screenshot_path))
            msg.attach(img)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, password)
            server.send_message(msg)
        print("[EMAIL] Alert sent successfully.")
    except Exception as e:
        print(f"[EMAIL] Failed: {e}")


def send_email_in_thread(screenshot_path=None):
    threading.Thread(
        target=send_email_alert,
        args=(screenshot_path,),
        daemon=True
    ).start()