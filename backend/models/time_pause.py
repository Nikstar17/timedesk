import uuid
from datetime import datetime, timezone
from sqlalchemy import Column,  DateTime, ForeignKey, Interval
from sqlalchemy.dialects.postgresql import UUID
from . import db


class TimePause(db.Model):
    __tablename__ = "time_pauses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    time_entries_id = Column(UUID(as_uuid=True), ForeignKey(
        'time_entries.id'), nullable=False)
    pause_start = Column(DateTime(timezone=True), nullable=False)
    pause_end = Column(DateTime(timezone=True))

    def __init__(self, time_entries_id: uuid.UUID, pause_start: datetime, pause_end: datetime | None = None):
        self.time_entries_id = time_entries_id
        self.pause_start = pause_start
        self.pause_end = pause_end
