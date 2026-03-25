import json
import os
import smtplib
import threading
from datetime import datetime
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def _load_saved_recipient():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    settings_path = os.path.join(project_root, 'backend', 'data', 'settings.json')
    if not os.path.exists(settings_path):
        return None

    try:
        with open(settings_path, 'r', encoding='utf-8') as fh:
            all_settings = json.load(fh)
    except (OSError, ValueError, json.JSONDecodeError):
        return None

    for settings in all_settings.values():
        recipient = str(settings.get('alert_email_recipient') or '').strip()
        if recipient:
            return recipient
    return None


def send_email_alert(screenshot_path=None, receiver_override=None):
    sender = os.environ.get('ALERT_EMAIL_SENDER')
    password = os.environ.get('ALERT_EMAIL_PASSWORD')
    receiver = receiver_override or os.environ.get('ALERT_EMAIL_RECEIVER') or _load_saved_recipient()

    if not all([sender, password, receiver]):
        print('[EMAIL] Skipped - email sender, password, or recipient is not configured.')
        return

    msg = MIMEMultipart()
    msg['Subject'] = 'AI Driver Safety Alert - Drowsiness Detected'
    msg['From'] = sender
    msg['To'] = receiver

    body = MIMEText(
        'Drowsiness detected at {time}.\n'
        'Please check on the driver immediately.\n\n'
        '- AI Driver Safety System'.format(
            time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ),
        'plain'
    )
    msg.attach(body)

    if screenshot_path and os.path.exists(screenshot_path):
        with open(screenshot_path, 'rb') as fh:
            img = MIMEImage(fh.read(), name=os.path.basename(screenshot_path))
            msg.attach(img)

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender, password)
            server.send_message(msg)
        print('[EMAIL] Alert sent successfully.')
    except Exception as exc:
        print(f'[EMAIL] Failed: {exc}')


def send_email_in_thread(screenshot_path=None, receiver_override=None):
    threading.Thread(
        target=send_email_alert,
        args=(screenshot_path, receiver_override),
        daemon=True
    ).start()
