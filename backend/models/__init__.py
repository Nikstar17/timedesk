from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Import models after db is defined to avoid circular imports
from .user import User  # noqa
from .project import Project  # noqa
from .time_entry import TimeEntry  # noqa
from .time_pause import TimePause  # noqa
