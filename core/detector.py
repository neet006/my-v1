import numpy as np
import mediapipe as mp

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=False,
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

LEFT_EYE_IDX  = [33, 160, 158, 133, 153, 144]
RIGHT_EYE_IDX = [362, 385, 387, 263, 373, 380]
MOUTH_IDX     = [61, 291, 13, 14, 78, 308]


def euclidean(p1, p2):
    return np.linalg.norm(np.array(p1) - np.array(p2))


def get_point(landmarks, idx, w, h):
    lm = landmarks[idx]
    return (int(lm.x * w), int(lm.y * h))


def eye_aspect_ratio(landmarks, eye_indices, w, h):
    pts = [get_point(landmarks, i, w, h) for i in eye_indices]
    A = euclidean(pts[1], pts[5])
    B = euclidean(pts[2], pts[4])
    C = euclidean(pts[0], pts[3])
    if C == 0:
        return 0.0
    return (A + B) / (2.0 * C)


def mouth_aspect_ratio(landmarks, mouth_indices, w, h):
    pts = [get_point(landmarks, i, w, h) for i in mouth_indices]
    A = euclidean(pts[2], pts[3])
    B = euclidean(pts[0], pts[1])
    if B == 0:
        return 0.0
    return A / B


def process_frame(frame):
    """
    Run MediaPipe on a BGR frame.
    Returns (results, h, w)
    """
    import cv2
    h, w, _ = frame.shape
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb)
    return results, h, w


def get_ear_mar(landmarks, w, h):
    """
    Returns (ear, mar) from face landmarks.
    """
    ear_l = eye_aspect_ratio(landmarks, LEFT_EYE_IDX, w, h)
    ear_r = eye_aspect_ratio(landmarks, RIGHT_EYE_IDX, w, h)
    ear   = (ear_l + ear_r) / 2.0
    mar   = mouth_aspect_ratio(landmarks, MOUTH_IDX, w, h)
    return ear, mar