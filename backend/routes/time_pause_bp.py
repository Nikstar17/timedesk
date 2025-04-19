from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from services.time_pause_service import start_time_pause, end_time_pause

time_pause_bp = Blueprint("time_pause_bp", __name__)


@time_pause_bp.route("/start-time-pause", methods=["POST"])
@jwt_required()
def start_time_pause_route():
    data = request.get_json()

    if data is None:
        return jsonify({"error": "Invalid JSON data"}), 400
    success, error = start_time_pause(time_entries_id=data["time_entries_id"])
    if success:
        return jsonify({"message": "Time pause started successfully"}), 200
    else:
        return jsonify({"error": error}), 400


@time_pause_bp.route("/end-time-pause", methods=["POST"])
@jwt_required()
def end_time_pause_route():
    data = request.get_json()

    if data is None:
        return jsonify({"error": "Invalid JSON data"}), 400

    success, error = end_time_pause(time_pause_id=data["time_pause_id"])

    if success:
        return jsonify({"message": "Time pause ended successfully"}), 200

    else:
        return jsonify({"error": error}), 400
