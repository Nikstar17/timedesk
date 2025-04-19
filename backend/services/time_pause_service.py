from models import db, TimePause
from datetime import datetime, timezone


def start_time_pause(time_entries_id):
    pause_start = datetime.now(timezone.utc)

    new_time_pause = TimePause(
        time_entries_id=time_entries_id, pause_start=pause_start)

    try:
        db.session.add(new_time_pause)
        db.session.commit()
        return True, None
    except Exception as e:
        db.session.rollback()
        return False, "Error starting pause"


def end_time_pause(time_pause_id):
    pause_end = datetime.now(timezone.utc)

    new_time_pause = TimePause.query.filter_by(
        id=time_pause_id).first()

    if new_time_pause is None:
        return False, "Time pause record not found"

    new_time_pause.pause_end = pause_end

    try:
        db.session.commit()
        return True, "Pause ended successfully"

    except Exception as e:
        db.session.rollback()
        return False, "Error ending pause"
