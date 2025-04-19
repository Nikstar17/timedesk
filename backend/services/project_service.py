from models import db, Project
from datetime import datetime


def create_project(name, description, user_id):
    new_project = Project(
        name=name,
        description=description,
        user_id=user_id
    )

    try:
        db.session.add(new_project)
        db.session.commit()
        return True, None
    except Exception as e:
        db.session.rollback()
        return False, str(e)


def get_projects_for_user(user_id):
    try:
        projects = Project.query.filter_by(user_id=user_id).all()
        result = [{
            "id": str(p.id),
            "name": p.name,
            "description": p.description,
            "created_at": p.created_at.isoformat()
        } for p in projects]
        return result, None
    except Exception as e:
        return None, str(e)


def delete_project(project_id, user_id):
    try:
        project = Project.query.filter_by(
            id=project_id, user_id=user_id).first()
        if project:
            db.session.delete(project)
            db.session.commit()
            return True, None
        else:
            return False, "Project not found or you do not have permission to delete it."
    except Exception as e:
        db.session.rollback()
        return False, str(e)
