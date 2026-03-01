from pathlib import Path

from ultralytics import YOLO

from agent.config import AgentConfig

PERSON_CLASS = 0


class PeopleTracker:
    """Tracks people across video frames using YOLOv8 object detection and tracking."""

    def __init__(self, config: AgentConfig):
        self.model = YOLO(config.yolo_model)
        self.confidence = config.yolo_confidence
        self.tracker_config = str(Path(__file__).parent / config.tracker_config)

    def track(self, frame) -> list[dict]:
        """
        Detect and track people in a video frame.

        Args:
            frame: Input image frame (numpy array or compatible format).

        Returns:
            List of detected people, each containing:
                - id (int): Persistent tracking ID across frames
                - center (tuple): (x, y) coordinates of person's bottom-center point
        """
        results = self.model.track(
            frame,
            persist=True,
            classes=[PERSON_CLASS],
            conf=self.confidence,
            device="cpu",
            verbose=False,
            tracker=self.tracker_config,
        )

        boxes = results[0].boxes
        if boxes.id is None:
            return []

        people = []
        for box, track_id in zip(boxes.xyxy, boxes.id):
            x1, y1, x2, y2 = box.tolist()
            center_x = (x1 + x2) / 2
            bottom_y = y2
            people.append({
                "id": int(track_id),
                "center": (center_x, bottom_y),
                "bbox": (int(x1), int(y1), int(x2), int(y2)),
            })

        return people
