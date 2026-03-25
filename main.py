import cv2
import time
import argparse
import numpy as np
from collections import deque

from core.detector  import process_frame, get_ear_mar
from core.scorer    import ear_to_score, classify_risk
from core.calibration import calibrate
from alerts.voice       import speak_alert_async
from alerts.email_alert import send_email_in_thread
from session.logger import SessionLogger
from session.report import save_session_report
from ui.hud         import draw_hud
from config.settings import (
    MAR_THRESHOLD, FRAME_CHECK, ALERT_COOLDOWN,
    SCREENSHOTS_DIR, REPORTS_DIR, RECORDINGS_DIR
)


def parse_args():
    parser = argparse.ArgumentParser(description="AI Driver Drowsiness Detection")
    parser.add_argument('--source',        default='0')
    parser.add_argument('--ear-threshold', type=float, default=None)
    parser.add_argument('--no-email',      action='store_true')
    parser.add_argument('--no-voice',      action='store_true')
    return parser.parse_args()


def main():
    args   = parse_args()
    source = int(args.source) if args.source.isdigit() else args.source

    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        print(f"[ERROR] Cannot open source: {args.source}")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    # Calibration
    if args.ear_threshold is not None:
        ear_threshold = args.ear_threshold
        open_ear_ref  = ear_threshold / 0.82
        print(f"[CONFIG] Manual EAR threshold: {ear_threshold}")
    else:
        ear_threshold, open_ear_ref = calibrate(cap, seconds=3)

    # State
    eye_counter  = 0
    yawn_counter = 0
    email_sent   = False

    ear_history = deque(maxlen=10)
    mar_history = deque(maxlen=5)
    logger      = SessionLogger()

    session_start = time.time()

    # Video writer
    import cv2 as _cv2
    fourcc = _cv2.VideoWriter_fourcc(*'XVID')
    out    = _cv2.VideoWriter(
        f'{RECORDINGS_DIR}/session_record.avi', fourcc, 20.0, (640, 480)
    )

    print("[SYSTEM] Monitoring started. Press Q to quit.\n")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame          = cv2.resize(frame, (640, 480))
        results, h, w  = process_frame(frame)
        elapsed        = time.time() - session_start

        if results.multi_face_landmarks:
            lms = results.multi_face_landmarks[0].landmark

            ear, mar = get_ear_mar(lms, w, h)

            ear_history.append(ear)
            mar_history.append(mar)
            smooth_ear = float(np.mean(ear_history))
            smooth_mar = float(np.mean(mar_history))

            yawning = smooth_mar > MAR_THRESHOLD
            if yawning:
                yawn_counter += 1
                if yawn_counter >= 10:
                    logger.log_yawn()
                    yawn_counter = 0
            else:
                yawn_counter = max(0, yawn_counter - 1)

            score         = ear_to_score(smooth_ear, open_ear_ref)
            if yawning and score >= 20:
                score = min(100, score + 15)

            status, color = classify_risk(score)
            logger.log_ear(elapsed, smooth_ear, score)

            # Eye counter
            if smooth_ear < ear_threshold:
                eye_counter += 1
            else:
                eye_counter = max(0, eye_counter - 1)

            # Trigger alert
            current_time = time.time()
            if eye_counter >= FRAME_CHECK:
                if current_time - (logger.alert_timestamps[-1] + session_start
                                   if logger.alert_timestamps else 0) > ALERT_COOLDOWN:

                    screenshot_path = logger.next_screenshot_path(SCREENSHOTS_DIR)
                    cv2.imwrite(screenshot_path, frame)
                    logger.log_alert(elapsed)

                    if not args.no_voice:
                        speak_alert_async()

                    if not email_sent and not args.no_email:
                        send_email_in_thread(screenshot_path)
                        email_sent = True

                    print(f"[ALERT] Drowsiness #{logger.drowsy_events} at {elapsed:.1f}s")

            frame = draw_hud(
                frame, ear, smooth_ear, score, status, color,
                eye_counter, logger.drowsy_events, logger.yawn_events,
                ear_threshold, smooth_mar, yawning
            )

            # Flashing red border on HIGH RISK
            if status == "HIGH RISK" and int(current_time * 2) % 2 == 0:
                cv2.rectangle(frame, (0, 0), (w - 1, h - 1), (0, 0, 255), 4)

        else:
            cv2.putText(frame, "NO FACE DETECTED", (200, 240),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (100, 100, 100), 2)

        out.write(frame)
        cv2.imshow("AI Driver Safety System", frame)

        if cv2.waitKey(1) & 0xFF in [ord('q'), ord('Q'), 27]:
            break

    # Cleanup
    session_duration = time.time() - session_start
    cap.release()
    out.release()
    cv2.destroyAllWindows()

    print(f"\n[SESSION] Duration: {session_duration:.1f}s | "
          f"Drowsy: {logger.drowsy_events} | Yawns: {logger.yawn_events}")

    save_session_report(logger, ear_threshold, session_duration, REPORTS_DIR)
    print("[DONE] Session ended.")


if __name__ == "__main__":
    main()