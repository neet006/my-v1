import cv2


def draw_hud(frame, ear, smooth_ear, score, status, color,
             eye_counter, drowsy_events, yawn_events,
             ear_threshold, mar, yawning):

    h, w = frame.shape[:2]
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (w, 35), (15, 15, 30), -1)
    cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)

    cv2.putText(frame, "AI DRIVER SAFETY SYSTEM",
                (int(w / 2) - 130, 23),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 220, 180), 2)

    info_lines = [
        (f"EAR (raw):    {ear:.3f}",       (200, 200, 200)),
        (f"EAR (smooth): {smooth_ear:.3f}", (200, 200, 200)),
        (f"Threshold:    {ear_threshold:.3f}", (150, 150, 255)),
        (f"MAR:          {mar:.3f}",        (200, 200, 200)),
        (f"Eye Counter:  {eye_counter}",    (200, 200, 200)),
    ]
    for i, (txt, col) in enumerate(info_lines):
        cv2.putText(frame, txt, (15, 65 + i * 28),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, col, 1)

    # Score bar
    bar_x, bar_y, bar_w, bar_h = 15, 215, 200, 20
    cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_w, bar_y + bar_h),
                  (50, 50, 50), -1)
    fill_w    = int(bar_w * score / 100)
    bar_color = (0, 200, 80) if score < 30 else ((0, 165, 255) if score < 60 else (0, 0, 255))
    cv2.rectangle(frame, (bar_x, bar_y), (bar_x + fill_w, bar_y + bar_h),
                  bar_color, -1)
    cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_w, bar_y + bar_h),
                  (150, 150, 150), 1)
    cv2.putText(frame, f"Drowsiness: {score}%", (bar_x, bar_y - 6),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (220, 220, 220), 1)

    # Status badge
    cv2.rectangle(frame, (15, 248), (225, 278), color, -1)
    cv2.putText(frame, f"STATUS: {status}", (23, 269),
                cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)

    cv2.putText(frame, f"Drowsy Alerts: {drowsy_events}", (15, 305),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (100, 180, 255), 1)
    cv2.putText(frame, f"Yawn Events:   {yawn_events}", (15, 330),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (100, 180, 255), 1)

    if yawning:
        cv2.putText(frame, "YAWNING DETECTED", (int(w / 2) - 110, h - 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)

    return frame