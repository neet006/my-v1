import threading
import time
from collections import deque

from alerts.email_alert import send_email_in_thread
from config.settings import ALERT_COOLDOWN, EAR_THRESHOLD, FRAME_CHECK, MAR_THRESHOLD
from session.logger import SessionLogger

CAMERA_IMPORT_ERROR = ""

try:
    import cv2  # type: ignore
    import numpy as np  # type: ignore
    from core.detector import get_ear_mar, process_frame
    from core.scorer import classify_risk, ear_to_score
    from ui.hud import draw_hud
except Exception as exc:  # pragma: no cover - fallback for missing native deps
    cv2 = None
    np = None
    get_ear_mar = None
    process_frame = None
    classify_risk = None
    ear_to_score = None
    draw_hud = None
    CAMERA_IMPORT_ERROR = str(exc)


class CameraMonitor:
    def __init__(self):
        self._lock = threading.Lock()
        self._thread = None
        self._running = False
        self._cap = None
        self._latest_frame = None
        self._status = self._default_status()
        self._ear_history = deque(maxlen=10)
        self._mar_history = deque(maxlen=5)
        self._open_eye_samples = []
        self._eye_counter = 0
        self._yawn_counter = 0
        self._logger = SessionLogger()
        self._session_started_at = None
        self._email_sent = False

    def _default_status(self):
        error = ""
        if not self.dependencies_ready():
            error = (
                "Camera dependencies are not installed or are incompatible with this Python version. "
                + CAMERA_IMPORT_ERROR
            ).strip()
        return {
            "running": False,
            "face_detected": False,
            "eye_status": "Waiting",
            "blink_rate": 0,
            "session_time": "00:00:00",
            "drowsiness": 0,
            "status": "IDLE",
            "ear": None,
            "mar": None,
            "threshold": EAR_THRESHOLD,
            "yawn_events": 0,
            "drowsy_events": 0,
            "sleep_events": 0,
            "recent_alerts": [],
            "error": error,
        }

    def dependencies_ready(self):
        return all([
            cv2 is not None,
            np is not None,
            get_ear_mar is not None,
            process_frame is not None,
            classify_risk is not None,
            ear_to_score is not None,
            draw_hud is not None,
        ])

    def start(self, source=0):
        with self._lock:
            if not self.dependencies_ready():
                self._status = self._default_status()
                return {"ok": False, "error": self._status["error"]}

            if self._running:
                return {"ok": True, "already_running": True}

            self._cap = cv2.VideoCapture(source)
            if not self._cap.isOpened():
                self._cap.release()
                self._cap = None
                self._status = self._default_status()
                self._status["error"] = "Could not open camera."
                return {"ok": False, "error": self._status["error"]}

            self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self._running = True
            self._latest_frame = None
            self._status = self._default_status()
            self._status["running"] = True
            self._status["error"] = ""
            self._session_started_at = time.time()
            self._ear_history.clear()
            self._mar_history.clear()
            self._open_eye_samples = []
            self._eye_counter = 0
            self._yawn_counter = 0
            self._logger = SessionLogger()
            self._email_sent = False
            self._thread = threading.Thread(target=self._run, daemon=True)
            self._thread.start()
            return {"ok": True, "already_running": False}

    def stop(self):
        with self._lock:
            if not self._running:
                summary = self._session_summary()
                summary["already_stopped"] = True
                return summary
            self._running = False
            cap = self._cap
            self._cap = None

        if cap is not None:
            cap.release()
        if self._thread is not None and self._thread.is_alive():
            self._thread.join(timeout=2)

        with self._lock:
            self._status["running"] = False
            summary = self._session_summary()
            self._latest_frame = None
            return summary

    def status(self):
        with self._lock:
            return dict(self._status)

    def frames(self):
        while True:
            with self._lock:
                running = self._running
                frame = self._latest_frame
                error = self._status.get("error", "")
            if frame is None:
                if not running and error:
                    time.sleep(0.5)
                else:
                    time.sleep(0.1)
                continue
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
            )

    def _push_alert(self, text):
        timestamp = time.strftime("%H:%M:%S")
        alerts = self._status["recent_alerts"]
        alerts.insert(0, f"{timestamp} - {text}")
        del alerts[5:]

    def _format_elapsed(self, elapsed):
        elapsed = max(0, int(elapsed))
        hours = elapsed // 3600
        minutes = (elapsed % 3600) // 60
        seconds = elapsed % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def _session_summary(self):
        elapsed = 0 if not self._session_started_at else time.time() - self._session_started_at
        hours = int(elapsed // 3600)
        minutes = int((elapsed % 3600) // 60)
        max_score = 0
        if self._logger.ear_log:
            max_score = max(int(entry[2]) for entry in self._logger.ear_log)
        status = "Completed"
        status_class = "completed"
        if max_score >= 80:
            status = "High Risk"
            status_class = "high-risk"
        elif max_score >= 60:
            status = "Drowsy"
            status_class = "completed-dark"
        return {
            "date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "duration": f"{hours}h {minutes:02d}m",
            "alerts": self._logger.drowsy_events,
            "max_drowsiness": f"{max_score}%",
            "status": status,
            "status_class": status_class,
            "drowsy_events": self._logger.drowsy_events,
            "sleep_events": self._status.get("sleep_events", 0),
            "yawn_events": self._logger.yawn_events,
        }

    def _run(self):
        while True:
            with self._lock:
                running = self._running
                cap = self._cap
            if not running or cap is None:
                break

            ok, frame = cap.read()
            if not ok:
                with self._lock:
                    self._status["error"] = "Camera frame read failed."
                time.sleep(0.1)
                continue

            frame = cv2.resize(frame, (640, 480))
            results, h, w = process_frame(frame)
            elapsed = 0 if not self._session_started_at else time.time() - self._session_started_at

            face_detected = False
            score = 0
            status_label = "IDLE"
            color = (100, 100, 100)
            blink_rate = 0
            eye_status = "Waiting"
            raw_ear = None
            smooth_mar = 0.0
            ear_threshold = EAR_THRESHOLD
            yawning = False
            sleep_events = self._status.get("sleep_events", 0)

            if results.multi_face_landmarks:
                face_detected = True
                landmarks = results.multi_face_landmarks[0].landmark
                raw_ear, mar = get_ear_mar(landmarks, w, h)
                self._ear_history.append(raw_ear)
                self._mar_history.append(mar)

                smooth_ear = float(np.mean(self._ear_history))
                smooth_mar = float(np.mean(self._mar_history))
                self._open_eye_samples.append(smooth_ear)
                if len(self._open_eye_samples) > 90:
                    self._open_eye_samples.pop(0)

                open_eye_ref = max(np.percentile(self._open_eye_samples, 80), EAR_THRESHOLD / 0.82)
                ear_threshold = max(EAR_THRESHOLD, round(open_eye_ref * 0.82, 3))
                score = ear_to_score(smooth_ear, open_eye_ref)

                yawning = smooth_mar > MAR_THRESHOLD
                if yawning:
                    self._yawn_counter += 1
                    if self._yawn_counter >= 10:
                        self._logger.log_yawn()
                        self._yawn_counter = 0
                else:
                    self._yawn_counter = max(0, self._yawn_counter - 1)

                if yawning and score >= 20:
                    score = min(100, score + 15)

                self._logger.log_ear(elapsed, smooth_ear, score)
                status_label, color = classify_risk(score)

                if smooth_ear < ear_threshold:
                    self._eye_counter += 1
                else:
                    self._eye_counter = max(0, self._eye_counter - 1)

                eye_status = "Closed" if smooth_ear < ear_threshold else "Open"
                blink_rate = int(max(8, min(32, round(18 - ((smooth_ear - ear_threshold) * 55)))))

                current_time = time.time()
                last_alert_elapsed = self._logger.alert_timestamps[-1] if self._logger.alert_timestamps else None
                enough_cooldown = last_alert_elapsed is None or (elapsed - last_alert_elapsed) > ALERT_COOLDOWN

                if self._eye_counter >= FRAME_CHECK and enough_cooldown:
                    self._logger.log_alert(elapsed)
                    self._push_alert(f"Drowsiness detected at {score}%")
                    if score >= 80:
                        sleep_events += 1
                    if not self._email_sent and score >= 80:
                        send_email_in_thread()
                        self._email_sent = True

                frame = draw_hud(
                    frame,
                    raw_ear,
                    smooth_ear,
                    score,
                    status_label,
                    color,
                    self._eye_counter,
                    self._logger.drowsy_events,
                    self._logger.yawn_events,
                    ear_threshold,
                    smooth_mar,
                    yawning,
                )
                if status_label == "HIGH RISK" and int(current_time * 2) % 2 == 0:
                    cv2.rectangle(frame, (0, 0), (w - 1, h - 1), (0, 0, 255), 4)
            else:
                self._eye_counter = 0
                cv2.putText(frame, "NO FACE DETECTED", (185, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (100, 100, 100), 2)

            success, encoded = cv2.imencode(".jpg", frame)
            if success:
                with self._lock:
                    self._latest_frame = encoded.tobytes()
                    self._status.update({
                        "running": self._running,
                        "face_detected": face_detected,
                        "eye_status": eye_status,
                        "blink_rate": blink_rate,
                        "session_time": self._format_elapsed(elapsed),
                        "drowsiness": int(score),
                        "status": status_label if self._running else "IDLE",
                        "ear": None if raw_ear is None else round(raw_ear, 3),
                        "mar": round(smooth_mar, 3) if face_detected else None,
                        "threshold": round(ear_threshold, 3),
                        "yawn_events": self._logger.yawn_events,
                        "drowsy_events": self._logger.drowsy_events,
                        "sleep_events": sleep_events,
                        "error": "",
                    })


camera_monitor = CameraMonitor()
