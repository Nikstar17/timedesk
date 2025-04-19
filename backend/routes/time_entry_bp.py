from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.time_entry_service import start_time_entry, stop_time_entry, get_active_time_entry, get_project_time_statistics, get_project_time_entries

time_entry_bp = Blueprint("time_entry_bp", __name__)


@time_entry_bp.route("/start-time-entry", methods=["POST"])
@jwt_required()
def start_time_entry_route():
    data = request.get_json()

    if data is None:
        return jsonify({"error": "Invalid JSON data"}), 400

    user_id = get_jwt_identity()
    success, error = start_time_entry(
        user_id=user_id, project_id=data["project_id"])
    if success:
        return jsonify({"message": "Time entry started successfully"}), 200
    else:
        return jsonify({"error": error}), 400


@time_entry_bp.route("/stop-time-entry", methods=["POST"])
@jwt_required()
def stop_time_entry_route():
    data = request.get_json()
    if data is None:
        return jsonify({"error": "Invalid JSON data"}), 400

    user_id = get_jwt_identity()

    success, error = stop_time_entry(
        user_id=user_id, time_entry_id=data["time_entry_id"])
    if success:
        return jsonify({"message": "Time entry stopped successfully"}), 200
    else:
        return jsonify({"error": error}), 400


@time_entry_bp.route("/active-time-entry", methods=["GET"])
@jwt_required()
def get_active_time_entry_route():
    user_id = get_jwt_identity()
    active_entry, error = get_active_time_entry(user_id)

    if error:
        return jsonify({"error": error}), 400

    if not active_entry:
        return jsonify({"active_entry": None}), 200

    return jsonify({"active_entry": active_entry}), 200


@time_entry_bp.route("/project-time-statistics", methods=["GET"])
@jwt_required()
def get_project_time_statistics_route():
    user_id = get_jwt_identity()
    statistics, error = get_project_time_statistics(user_id)

    if error:
        return jsonify({"error": error}), 400

    return jsonify({"statistics": statistics}), 200


@time_entry_bp.route("/project/<project_id>/time-entries", methods=["GET"])
@jwt_required()
def get_project_time_entries_route(project_id):
    user_id = get_jwt_identity()
    entries, error = get_project_time_entries(user_id, project_id)

    if error:
        return jsonify({"error": error}), 400

    return jsonify({"entries": entries}), 200
