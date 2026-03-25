import os
from dotenv import load_dotenv
load_dotenv()

EAR_THRESHOLD   = float(os.getenv("EAR_THRESHOLD", 0.23))
MAR_THRESHOLD   = float(os.getenv("MAR_THRESHOLD", 0.55))
FRAME_CHECK     = int(os.getenv("FRAME_CHECK", 15))
ALERT_COOLDOWN  = int(os.getenv("ALERT_COOLDOWN", 5))

EMAIL_SENDER    = os.getenv("ALERT_EMAIL_SENDER")
EMAIL_PASSWORD  = os.getenv("ALERT_EMAIL_PASSWORD")
EMAIL_RECEIVER  = os.getenv("ALERT_EMAIL_RECEIVER")

DATA_DIR        = "data"
SCREENSHOTS_DIR = f"{DATA_DIR}/screenshots"
REPORTS_DIR     = f"{DATA_DIR}/reports"
RECORDINGS_DIR  = f"{DATA_DIR}/recordings"



# =========================
# .env.example (configuration file)
# Commit this file, NEVER commit actual .env
# =========================
# ALERT_EMAIL_SENDER=yourmail@gmail.com
# ALERT_EMAIL_PASSWORD=your_app_password
# ALERT_EMAIL_RECEIVER=receiver@gmail.com
# EAR_THRESHOLD=0.23
# FRAME_CHECK=15
# ALERT_COOLDOWN=5


# =========================
# .gitignore (Git config file)
# Files/folders to ignore in version control
# =========================
# .env
# data/
# __pycache__/
# *.pyc
# *.avi
# *.jpg
# *.png
# session_report_*


# =========================
# requirements.txt (dependencies list)
# Install using: pip install -r requirements.txt
# =========================
# opencv-python==4.9.0.80
# mediapipe==0.10.9
# numpy==1.26.4
# pyttsx3==2.90
# matplotlib==3.8.4
# python-dotenv==1.0.1