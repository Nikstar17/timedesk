import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from . import db


class Project(db.Model):
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey(
        "users.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False,
                        default=lambda: datetime.now(timezone.utc))
    time_entries = relationship(
        "TimeEntry", backref="project", cascade="all, delete-orphan")

    def __init__(self, user_id: uuid.UUID, name: str, description: str | None = None):
        self.user_id = user_id
        self.name = name
        self.description = description

    def __repr__(self) -> str:
        return f"<Project {self.name}>"
