from sqlalchemy.orm import Session

from app.core.preprocessor import preprocess
from app.core.detector import PeopleDetector
from app.db.repository import PeopleCountRepository


class PipelineService:
    def __init__(self, db: Session, detector: PeopleDetector):
        self.detector = detector
        self.repository = PeopleCountRepository(db)

    def process(self, image_bytes: bytes, camera_id: str, event: str = "snapshot") -> int:
        result = preprocess(image_bytes)
        detection = self.detector.detect(result.frame)
        self.repository.create(
            camera_id=camera_id,
            people_count=detection.count,
            event=event,
        )
        return detection.count
