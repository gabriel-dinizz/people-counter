from fastapi import APIRouter, Depends, Form, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.repository import CrossingEventRepository

router = APIRouter()


@router.post("/events")
def create_event(
    camera_id: str = Form(...),
    direction: str = Form(...),
    db: Session = Depends(get_db),
):
    """Record a crossing event reported by an edge agent.

    Args:
        camera_id: Identifier of the reporting camera.
        direction: ``"entry"`` or ``"exit"``.
        db: Database session (injected).

    Returns:
        Dict with ``camera_id``, ``direction``, and ``timestamp`` of the
        persisted event.

    Raises:
        HTTPException: 422 if *direction* is not ``"entry"`` or ``"exit"``.
    """
    if direction not in ("entry", "exit"):
        raise HTTPException(status_code=422, detail="direction must be 'entry' or 'exit'")
    repo = CrossingEventRepository(db)
    event = repo.create(camera_id=camera_id, direction=direction)
    return {"camera_id": event.camera_id, "direction": event.direction, "timestamp": event.timestamp}


@router.get("/occupancy/{camera_id}")
def get_occupancy(camera_id: str, db: Session = Depends(get_db)):
    """Return the current occupancy for a given camera.

    Args:
        camera_id: The camera to query.
        db: Database session (injected).

    Returns:
        Dict with ``camera_id`` and ``occupancy`` (int, >= 0).
    """
    repo = CrossingEventRepository(db)
    return {"camera_id": camera_id, "occupancy": repo.get_occupancy(camera_id)}
