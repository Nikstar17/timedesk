from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, jwt_required, get_jwt_identity, set_access_cookies, unset_jwt_cookies)
from services.user_service import register_user, login_user

user_bp = Blueprint("user_bp", __name__)


@user_bp.route("/register", methods=["POST"])
def register_user_route():
    data = request.get_json()
    if not data or "email" not in data or "password" not in data:
        return jsonify({"error": "Invalid or missing JSON data"}), 400

    success, error = register_user(data["email"], data["password"])
    if success:
        return jsonify({"message": "User successfully registered"}), 201
    else:
        return jsonify({"error": f"An error occurred while registering user: {error}"}), 500


@user_bp.route("/login", methods=["POST"])
def login_user_route():
    data = request.get_json()

    if not data or "email" not in data or "password" not in data:
        return jsonify({"error": "Invalid or missing JSON data"}), 400

    success, result = login_user(
        email=data["email"], password=data["password"])

    if success:
        return result
    else:
        return jsonify({"error": result}), 401


@user_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh_token():
    current_user_id = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user_id)

    response = jsonify({"access_token": new_access_token})
    set_access_cookies(response, new_access_token)
    return response


@user_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout_user_route():
    response = jsonify({"message": "Logout successful"})
    unset_jwt_cookies(response)
    return response


@user_bp.route("/auth/check", methods=["GET"])
@jwt_required()
def auth_check_route():
    return jsonify({"msg": "Authenticated"}), 200
