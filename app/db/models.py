from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime

from app.db.database import Base


class CrossingEvent(Base):
    __tablename__ = "crossing_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    camera_id = Column(String(64), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    direction = Column(String(8), nullable=False)  # "entry" or "exit"
