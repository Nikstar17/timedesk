from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.project_service import create_project, get_projects_for_user, delete_project

project_bp = Blueprint("project_bp", __name__)


@project_bp.route("/project", methods=["POST"])
@jwt_required()
def create_project_route():
    data = request.get_json()
    if data is None:
        return jsonify({"error": "Invalid JSON data"}), 400

    current_user_id = get_jwt_identity()
    success, error = create_project(
        data["name"], data["description"], current_user_id)

    if success:
        return jsonify({"message": "Project registered successfully"}), 201
    else:
        return jsonify({"error": f"An error occurred while adding project: {error}"}), 500


@project_bp.route("/project", methods=["GET"])
@jwt_required()
def get_user_projects():
    current_user_id = get_jwt_identity()
    projects, error = get_projects_for_user(current_user_id)

    if error:
        return jsonify({"error": f"An error occurred while fetching projects: {error}"}), 500

    return jsonify({"projects": projects}), 200


@project_bp.route("/project/<uuid:project_uuid>", methods=['DELETE'])
@jwt_required()
def delete_project_route(project_uuid):
    user_id = get_jwt_identity()
    success, error = delete_project(str(project_uuid), user_id)

    if success:
        return jsonify({"message": "Project deleted successfully"}), 200
    else:
        return jsonify({"error": f"An error occurred while deleting project: {error}"}), 500
