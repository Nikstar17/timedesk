from models import db, TimeEntry
from datetime import datetime, timezone, timedelta
from sqlalchemy import desc, func
from uuid import UUID


def start_time_entry(user_id, project_id):
    start_time = datetime.now(timezone.utc)
    new_time_entry = TimeEntry(
        user_id=user_id,
        project_id=project_id,
        start_time=start_time
    )

    try:
        db.session.add(new_time_entry)
        db.session.commit()
        return True, None

    except Exception:
        db.session.rollback()
        return False, str("Error starting time entry")


def stop_time_entry(user_id, time_entry_id):
    try:
        user_id = UUID(user_id)
    except ValueError:
        return False, "Invalid user ID format"

    time_entry = TimeEntry.query.filter_by(id=time_entry_id).first()

    if time_entry is None:
        return False, "TimeEntryID not found"

    if time_entry.user_id != user_id:
        print(user_id)
        return False, "This time entry does not belong to this user"

    time_entry.end_time = datetime.now(timezone.utc)

    try:
        db.session.commit()
        return True, None

    except Exception as e:
        db.session.rollback()
        return False, "Error stopping time entry"


def get_active_time_entry(user_id):
    """Get the active time entry for a user"""
    try:
        if isinstance(user_id, str):
            user_id = UUID(user_id)
    except ValueError:
        return None, "Invalid user ID format"

    try:
        # Find time entry that has a start time but no end time
        active_entry = (TimeEntry.query
                        .filter_by(user_id=user_id, end_time=None)
                        .order_by(desc('start_time'))
                        .first())

        if active_entry:
            # Get active pause if any
            from models import TimePause
            active_pause = TimePause.query.filter_by(
                time_entries_id=active_entry.id,
                pause_end=None
            ).first()

            return {
                "id": str(active_entry.id),
                "project_id": str(active_entry.project_id),
                "start_time": active_entry.start_time.isoformat(),
                "is_paused": active_pause is not None,
                "pause_id": str(active_pause.id) if active_pause else None
            }, None
        else:
            return None, None
    except Exception as e:
        return None, str(e)


def get_project_time_statistics(user_id):
    """Get time statistics for all projects of a user"""
    try:
        if isinstance(user_id, str):
            user_id = UUID(user_id)
    except ValueError:
        return None, "Invalid user ID format"

    try:
        # Get all the user's projects with their time entries
        from models import Project, TimePause
        from sqlalchemy.orm import joinedload

        projects = Project.query.filter_by(user_id=user_id).all()

        result = {}
        for project in projects:
            project_id = str(project.id)
            result[project_id] = {
                "total_time": timedelta(0),
                "total_pause_time": timedelta(0),
                "active_time": None,
                "active_since": None,
                "is_active": False,
                "is_paused": False,
                "current_session_time": None
            }

            # Get completed time entries (have end_time)
            completed_entries = TimeEntry.query.filter_by(
                user_id=user_id,
                project_id=project.id
            ).filter(TimeEntry.end_time.isnot(None)).all()  # type: ignore

            # Calculate total time for completed entries
            for entry in completed_entries:
                # Calculate entry duration
                duration = entry.end_time - entry.start_time

                # Subtract pause time
                pauses = TimePause.query.filter_by(
                    time_entries_id=entry.id).all()
                pause_duration = timedelta(0)
                for pause in pauses:
                    if pause.pause_start and pause.pause_end:
                        pause_duration += pause.pause_end - pause.pause_start

                result[project_id]["total_pause_time"] += pause_duration
                result[project_id]["total_time"] += (duration - pause_duration)

            # Check for active time entry
            active_entry = TimeEntry.query.filter_by(
                user_id=user_id,
                project_id=project.id,
                end_time=None
            ).first()

            if active_entry:
                result[project_id]["is_active"] = True
                result[project_id]["active_since"] = active_entry.start_time.isoformat()

                # Calculate current session time
                now = datetime.now(timezone.utc)
                current_duration = now - active_entry.start_time

                # Check if currently paused
                active_pause = TimePause.query.filter_by(
                    time_entries_id=active_entry.id,
                    pause_end=None
                ).first()

                if active_pause:
                    result[project_id]["is_paused"] = True
                    pause_duration = now - active_pause.pause_start
                    current_duration -= pause_duration

                # Get all completed pauses for this active entry
                completed_pauses = TimePause.query.filter_by(
                    time_entries_id=active_entry.id
                ).filter(TimePause.pause_end.isnot(None)).all()  # type: ignore

                total_pause = timedelta(0)
                for pause in completed_pauses:
                    total_pause += pause.pause_end - pause.pause_start

                # Subtract completed pauses from current duration
                current_duration -= total_pause

                result[project_id]["current_session_time"] = {
                    "hours": current_duration.seconds // 3600,
                    "minutes": (current_duration.seconds % 3600) // 60,
                    "seconds": current_duration.seconds % 60
                }

        # Convert timedeltas to hours, minutes, seconds dictionaries
        for project_id, stats in result.items():
            total_seconds = int(stats["total_time"].total_seconds())
            stats["total_time"] = {
                "hours": total_seconds // 3600,
                "minutes": (total_seconds % 3600) // 60,
                "seconds": total_seconds % 60
            }

            pause_seconds = int(stats["total_pause_time"].total_seconds())
            stats["total_pause_time"] = {
                "hours": pause_seconds // 3600,
                "minutes": (pause_seconds % 3600) // 60,
                "seconds": pause_seconds % 60
            }

        return result, None
    except Exception as e:
        return None, str(e)


def get_project_time_entries(user_id, project_id):
    """Get all time entries for a specific project"""
    try:
        if isinstance(user_id, str):
            user_id = UUID(user_id)
        if isinstance(project_id, str):
            project_id = UUID(project_id)
    except ValueError:
        return None, "Invalid ID format"

    try:
        # Check if project belongs to user
        from models import Project
        project = Project.query.filter_by(
            id=project_id, user_id=user_id).first()
        if not project:
            return None, "Project not found or does not belong to user"

        # Get all time entries for the project
        from models import TimeEntry, TimePause
        from sqlalchemy.orm import joinedload

        entries = TimeEntry.query.filter_by(
            user_id=user_id,
            project_id=project_id
        ).order_by(TimeEntry.start_time.desc()).all()  # type: ignore

        result = []
        for entry in entries:
            # Get pauses for this entry
            pauses = TimePause.query.filter_by(time_entries_id=entry.id).all()

            # Calculate total pause duration
            total_pause_duration = timedelta(0)
            for pause in pauses:
                if pause.pause_start and pause.pause_end:
                    total_pause_duration += pause.pause_end - pause.pause_start

            # Calculate effective duration (entry duration minus pauses)
            if entry.end_time:
                entry_duration = entry.end_time - entry.start_time
                effective_duration = entry_duration - total_pause_duration
            else:
                # For active entries, calculate duration until now
                now = datetime.now(timezone.utc)
                entry_duration = now - entry.start_time

                # Check if currently paused
                active_pause = next(
                    (p for p in pauses if p.pause_end is None), None)
                if active_pause:
                    # Subtract time from pause start until now
                    pause_duration = now - active_pause.pause_start
                    total_pause_duration += pause_duration

                effective_duration = entry_duration - total_pause_duration

            # Convert timedeltas to seconds
            entry_duration_seconds = int(entry_duration.total_seconds())
            pause_duration_seconds = int(total_pause_duration.total_seconds())
            effective_duration_seconds = int(
                effective_duration.total_seconds())

            # Format pause information
            formatted_pauses = []
            for pause in pauses:
                if pause.pause_start:
                    pause_info = {
                        "id": str(pause.id),
                        "start_time": pause.pause_start.isoformat(),
                        "end_time": pause.pause_end.isoformat() if pause.pause_end else None,
                        "is_active": pause.pause_end is None
                    }
                    formatted_pauses.append(pause_info)

            # Create entry object
            entry_info = {
                "id": str(entry.id),
                "start_time": entry.start_time.isoformat(),
                "end_time": entry.end_time.isoformat() if entry.end_time else None,
                "is_active": entry.end_time is None,
                "total_duration": {
                    "hours": entry_duration_seconds // 3600,
                    "minutes": (entry_duration_seconds % 3600) // 60,
                    "seconds": entry_duration_seconds % 60
                },
                "pause_duration": {
                    "hours": pause_duration_seconds // 3600,
                    "minutes": (pause_duration_seconds % 3600) // 60,
                    "seconds": pause_duration_seconds % 60
                },
                "effective_duration": {
                    "hours": effective_duration_seconds // 3600,
                    "minutes": (effective_duration_seconds % 3600) // 60,
                    "seconds": effective_duration_seconds % 60
                },
                "pauses": formatted_pauses
            }

            result.append(entry_info)

        return result, None
    except Exception as e:
        return None, str(e)
