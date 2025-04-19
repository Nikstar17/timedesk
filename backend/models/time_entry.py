import uuid
from datetime import datetime, timezone, timedelta
from typing import cast
from sqlalchemy import Column, DateTime, ForeignKey, Interval
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from . import db


class TimeEntry(db.Model):
    __tablename__ = "time_entries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey(
        "users.id"), nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey(
        "projects.id"), nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True))
    duration = Column(Interval)
    created_at = Column(DateTime(timezone=True), nullable=False,
                        default=lambda: datetime.now(timezone.utc))
    pauses = relationship("TimePause", backref="time_entry",
                          cascade="all, delete-orphan")

    def __init__(
        self,
        user_id: uuid.UUID,
        project_id: uuid.UUID,
        start_time: datetime,
        end_time: datetime | None = None,
        duration: datetime | None = None,
    ):
        self.user_id = user_id
        self.project_id = project_id
        self.start_time = start_time
        self.end_time = end_time
        self.duration = duration

    def __repr__(self) -> str:
        return f"<TimeEntry {self.start_time} - {self.end_time}>"

    def calculate_duration(self) -> timedelta:
        end_time = cast(datetime, self.end_time)
        start_time = cast(datetime, self.start_time)

        if end_time is None or start_time is None:
            return timedelta()

        total_pause = timedelta()
        for pause in self.pauses:
            if pause.pause_start and pause.pause_end:
                total_pause += pause.pause_end - pause.pause_start

        return end_time - start_time - total_pause
