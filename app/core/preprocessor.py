from dataclasses import dataclass, field

import cv2
import numpy as np

BRIGHTNESS_THRESHOLD = 50.0  # mean pixel value (0–255); below this is considered too dark
BLUR_THRESHOLD = 100.0       # Laplacian variance; below this is considered too blurry


@dataclass
class PreprocessResult:
    frame: np.ndarray
    enhancements: list[str] = field(default_factory=list)  # e.g. ["brightness", "sharpness"]


def preprocess(image_bytes: bytes) -> PreprocessResult:
    nparr = np.frombuffer(image_bytes, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if frame is None:
        raise ValueError("Could not decode image bytes — unsupported format or corrupted data")

    enhancements = []
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    if gray.mean() < BRIGHTNESS_THRESHOLD:
        lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        frame = cv2.cvtColor(cv2.merge((l, a, b)), cv2.COLOR_LAB2BGR)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # recompute after brightness fix
        enhancements.append("brightness")

    if cv2.Laplacian(gray, cv2.CV_64F).var() < BLUR_THRESHOLD:
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
        frame = cv2.filter2D(frame, -1, kernel)
        enhancements.append("sharpness")

    return PreprocessResult(frame=frame, enhancements=enhancements)
