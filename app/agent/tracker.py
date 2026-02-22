from ultralytics import YOLO

from agent.config import AgentConfig

PERSON_CLASS = 0


class PeopleTracker:
    def __init__(self, config: AgentConfig):
        self.model = YOLO(config.yolo_model)
        self.confidence = config.yolo_confidence

    def track(self, frame) -> list[dict]:
        results = self.model.track(
            frame,
            persist=True,
            classes=[PERSON_CLASS],
            conf=self.confidence,
            device="cpu",
            verbose=False,
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
            })

        return people
