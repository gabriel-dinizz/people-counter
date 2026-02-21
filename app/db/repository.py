from typing import Generic, TypeVar, Type, List, Optional
from datetime import datetime

from sqlalchemy.orm import Session

from app.db.database import Base
from app.db.models import PeopleCount

T = TypeVar("T", bound=Base)


class BaseRepository(Generic[T]):
    """Base repository with common CRUD operations."""

    def __init__(self, model: Type[T], db: Session):
        self.model = model
        self.db = db

    def create(self, **kwargs) -> T:
        """Create a new record."""
        instance = self.model(**kwargs)
        self.db.add(instance)
        self.db.commit()
        self.db.refresh(instance)
        return instance

    def get_by_id(self, id: int) -> Optional[T]:
        """Get a record by ID."""
        return self.db.query(self.model).filter(self.model.id == id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """Get all records with pagination."""
        return self.db.query(self.model).offset(skip).limit(limit).all()


class PeopleCountRepository(BaseRepository[PeopleCount]):
    """Repository for PeopleCount model."""

    def __init__(self, db: Session):
        super().__init__(PeopleCount, db)

    def get_by_camera_id(
        self, camera_id: str, skip: int = 0, limit: int = 100
    ) -> List[PeopleCount]:
        """Get all counts for a specific camera."""
        return (
            self.db.query(PeopleCount)
            .filter(PeopleCount.camera_id == camera_id)
            .order_by(PeopleCount.timestamp.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_date_range(
        self, start_date: datetime, end_date: datetime, camera_id: Optional[str] = None
    ) -> List[PeopleCount]:
        """Get counts within a date range, optionally filtered by camera."""
        query = self.db.query(PeopleCount).filter(
            PeopleCount.timestamp >= start_date, PeopleCount.timestamp <= end_date
        )
        if camera_id:
            query = query.filter(PeopleCount.camera_id == camera_id)
        return query.order_by(PeopleCount.timestamp.desc()).all()

    def get_latest_by_camera(self, camera_id: str) -> Optional[PeopleCount]:
        """Get the most recent count for a specific camera."""
        return (
            self.db.query(PeopleCount)
            .filter(PeopleCount.camera_id == camera_id)
            .order_by(PeopleCount.timestamp.desc())
            .first()
        )
