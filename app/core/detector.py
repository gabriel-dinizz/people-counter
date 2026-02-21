from dataclasses import dataclass

import numpy as np
from ultralytics import YOLO

from app.config import settings

PERSON_CLASS_ID = 0  # COCO dataset: class 0 = person


@dataclass
class DetectionResult:
    count: int
    boxes: list[list[float]]  # [[x1, y1, x2, y2], ...]
    confidences: list[float]


class PeopleDetector:
    def __init__(self):
        self.model = YOLO(settings.YOLO_MODEL)
        self.confidence = settings.YOLO_CONFIDENCE
        self.device = settings.YOLO_DEVICE

    def detect(self, frame: np.ndarray) -> DetectionResult:
        results = self.model(
            frame,
            conf=self.confidence,
            classes=[PERSON_CLASS_ID],
            device=self.device,
            verbose=False,
        )
        boxes = results[0].boxes
        return DetectionResult(
            count=len(boxes),
            boxes=boxes.xyxy.tolist(),
            confidences=boxes.conf.tolist(),
        )
