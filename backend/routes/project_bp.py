from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Project, User

project_bp = Blueprint("project_bp", __name__)


@project_bp.route("/project", methods=["POST"])
@jwt_required()
def create_project():
    data = request.get_json()

    if data is None:
        return jsonify({"error": "Invalid JSON data"}), 400

    current_user_id = get_jwt_identity()

    new_project = Project()
    new_project.name = data["name"]
    new_project.description = data["description"]
    new_project.user_id = current_user_id

    try:
        db.session.add(new_project)
        db.session.commit()

        return (jsonify({"message": "Project registered successfully"}), 201,)

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "An error occurred while adding Project: " + str(e)}), 500


@project_bp.route("/project", methods=["GET"])
@jwt_required()
def get_user_projects():
    current_user_id = get_jwt_identity()

    try:
        projects = Project.query.filter_by(user_id=current_user_id).all()

        projects_list = []
        for project in projects:
            projects_list.append({
                "id": str(project.id),
                "name": project.name,
                "description": project.description,
                "created_at": project.created_at.isoformat()
            })

        return jsonify({"projects": projects_list}), 200

    except Exception as e:
        return jsonify({"error": "An error occurred while fetching projects: " + str(e)}), 500
