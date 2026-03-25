# 🚗 AI Driver Safety System

A real-time driver drowsiness detection system using computer vision and facial landmark analysis. Built with MediaPipe, OpenCV, and Python.

## Features

- 👁️ Eye Aspect Ratio (EAR) based drowsiness detection
- 😮 Yawn detection via Mouth Aspect Ratio (MAR)
- 🎯 Per-driver calibration at startup
- 🔊 Non-blocking voice alerts
- 📧 Email alerts with screenshot attached
- 📊 Session report with EAR timeline and drowsiness score charts
- 🎥 Session video recording

## Project Structure
```
driver-safety-system/
├── core/          # Detection engine (EAR, MAR, calibration, scoring)
├── alerts/        # Voice, email, and buzzer alert handlers
├── session/       # Session logger and report generator
├── ui/            # HUD overlay drawing
├── config/        # Settings and environment variables
├── tests/         # Unit tests
├── data/          # Runtime output (gitignored)
└── main.py        # Entry point
```

## Setup

**1. Clone the repo**
```bash
git clone https://github.com/Harshith-005/driver-safety-system.git
cd driver-safety-system
```

**2. Create virtual environment**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Configure environment variables**
```bash
cp .env.example .env
```
Fill in your Gmail credentials in `.env`:
```
ALERT_EMAIL_SENDER=yourgmail@gmail.com
ALERT_EMAIL_PASSWORD=your_app_password
ALERT_EMAIL_RECEIVER=receiver@gmail.com
```

## Usage
```bash
# Run with webcam (default)
python main.py

# Run on a video file
python main.py --source path/to/video.mp4

# Disable alerts for testing
python main.py --no-email --no-voice

# Manual EAR threshold override
python main.py --ear-threshold 0.21
```

## How It Works

1. At startup, a **3-second calibration** measures your natural open-eye EAR
2. The system sets the drowsiness threshold to **82% of your calibrated EAR**
3. EAR and MAR are tracked every frame and smoothed over a rolling window
4. If EAR stays below threshold for 15+ consecutive frames → alert triggered
5. Yawning compounds the drowsiness score by +15 points
6. On session end, a full report is saved to `data/reports/`

## Requirements

- Python 3.8 – 3.11
- Webcam
- Gmail account with App Password enabled (for email alerts)

## Tech Stack

- [MediaPipe](https://mediapipe.dev/) — Face mesh landmarks
- [OpenCV](https://opencv.org/) — Video capture and display
- [pyttsx3](https://pypi.org/project/pyttsx3/) — Text-to-speech alerts
- [Matplotlib](https://matplotlib.org/) — Session report charts
