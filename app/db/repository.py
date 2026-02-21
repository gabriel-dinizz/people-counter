from typing import List

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.models import CrossingEvent


class CrossingEventRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, camera_id: str, direction: str) -> CrossingEvent:
        event = CrossingEvent(camera_id=camera_id, direction=direction)
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event

    def get_occupancy(self, camera_id: str) -> int:
        entries = self.db.query(func.count(CrossingEvent.id)).filter(
            CrossingEvent.camera_id == camera_id,
            CrossingEvent.direction == "entry",
        ).scalar() or 0
        exits = self.db.query(func.count(CrossingEvent.id)).filter(
            CrossingEvent.camera_id == camera_id,
            CrossingEvent.direction == "exit",
        ).scalar() or 0
        return max(0, entries - exits)

    def get_by_camera(self, camera_id: str, limit: int = 100) -> List[CrossingEvent]:
        return (
            self.db.query(CrossingEvent)
            .filter(CrossingEvent.camera_id == camera_id)
            .order_by(CrossingEvent.timestamp.desc())
            .limit(limit)
            .all()
        )
