def ear_to_score(smooth_ear, open_ear, closed_ear=0.15):
    """
    Normalize EAR to a 0–100 drowsiness score.
    100 = fully closed, 0 = fully open.
    """
    if open_ear <= closed_ear:
        open_ear = closed_ear + 0.01
    score = (open_ear - smooth_ear) / (open_ear - closed_ear)
    return int(max(0, min(100, score * 100)))


def classify_risk(score):
    """
    Returns (status_string, BGR_color)
    """
    if score < 30:
        return "SAFE",      (0, 200, 80)
    elif score < 60:
        return "WARNING",   (0, 165, 255)
    else:
        return "HIGH RISK", (0, 0, 255)