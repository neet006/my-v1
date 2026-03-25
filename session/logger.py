class SessionLogger:
    def __init__(self):
        self.ear_log          = []   # (timestamp, ear, score)
        self.alert_timestamps = []   # seconds elapsed at each alert
        self.drowsy_events    = 0
        self.yawn_events      = 0
        self.screenshot_count = 0

    def log_ear(self, elapsed, smooth_ear, score):
        self.ear_log.append((elapsed, smooth_ear, score))

    def log_alert(self, elapsed):
        self.alert_timestamps.append(elapsed)
        self.drowsy_events += 1

    def log_yawn(self):
        self.yawn_events += 1

    def next_screenshot_path(self, folder="data/screenshots"):
        path = f"{folder}/alert_{self.screenshot_count}.jpg"
        self.screenshot_count += 1
        return path