from typing import List

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.models import CrossingEvent


class CrossingEventRepository:
    """Data-access layer for crossing events.

    Encapsulates all database queries related to ``CrossingEvent``,
    keeping business logic out of the route handlers.

    Args:
        db: An active SQLAlchemy session.
    """

    def __init__(self, db: Session):
        self.db = db

    def create(self, camera_id: str, direction: str) -> CrossingEvent:
        """Persist a new crossing event and return the committed row.

        Args:
            camera_id: Identifier of the camera that observed the crossing.
            direction: ``"entry"`` or ``"exit"``.

        Returns:
            The newly created ``CrossingEvent`` with its generated
            ``id`` and ``timestamp``.
        """
        event = CrossingEvent(camera_id=camera_id, direction=direction)
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event

    def get_occupancy(self, camera_id: str) -> int:
        """Calculate the current occupancy for a camera.

        Computed as ``max(0, entries - exits)`` across all recorded
        events. Returns zero if exits exceed entries.

        Args:
            camera_id: The camera to query.

        Returns:
            The estimated number of people currently inside.
        """
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
        """Fetch the most recent crossing events for a camera.

        Args:
            camera_id: The camera to query.
            limit: Maximum number of events to return (default 100).

        Returns:
            Events ordered by timestamp descending.
        """
        return (
            self.db.query(CrossingEvent)
            .filter(CrossingEvent.camera_id == camera_id)
            .order_by(CrossingEvent.timestamp.desc())
            .limit(limit)
            .all()
        )
