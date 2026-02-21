from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime

from app.db.database import Base


class PeopleCount(Base):
    __tablename__ = "people_counts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    camera_id = Column(String(64), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    people_count = Column(Integer, nullable=False)
    event = Column(String(64), nullable=False, default="snapshot")
