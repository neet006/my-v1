import cv2
import numpy as np
import time
from core.detector import process_frame, get_ear_mar


def calibrate(cap, seconds=3):
    """
    Collect EAR samples while driver keeps eyes open.
    Returns recommended EAR threshold = 82% of natural open-eye EAR.
    """
    print(f"\n[CALIBRATION] Keep your eyes OPEN. Calibrating for {seconds} seconds...\n")
    samples = []
    start   = time.time()

    while time.time() - start < seconds:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.resize(frame, (640, 480))
        results, h, w = process_frame(frame)
        remaining = int(seconds - (time.time() - start)) + 1

        cv2.putText(frame, f"CALIBRATING... {remaining}s", (150, 240),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 3)
        cv2.putText(frame, "Keep your eyes WIDE OPEN", (110, 290),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        if results.multi_face_landmarks:
            lms = results.multi_face_landmarks[0].landmark
            ear, _ = get_ear_mar(lms, w, h)
            samples.append(ear)

        cv2.imshow("Calibrating...", frame)
        cv2.waitKey(1)

    cv2.destroyAllWindows()

    if len(samples) < 5:
        print("[CALIBRATION] Not enough samples. Using default threshold: 0.23")
        return 0.23, 0.23 / 0.82

    mean_ear  = np.mean(samples)
    threshold = round(mean_ear * 0.82, 3)
    print(f"[CALIBRATION] Mean EAR: {mean_ear:.3f} → Threshold: {threshold}\n")
    return threshold, mean_ear