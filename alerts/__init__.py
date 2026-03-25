from alerts.buzzer import buzz_alert
from alerts.email_alert import send_email_in_thread


def speak_alert_async(message="Warning. Driver is sleeping. Please wake up immediately."):
    from alerts.voice import speak_alert_async as _speak_alert_async

    return _speak_alert_async(message)
