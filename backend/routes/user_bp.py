from flask import Blueprint, request, jsonify
from flask_jwt_extended import (create_access_token, jwt_required, get_jwt_identity,
                                create_refresh_token, set_access_cookies, set_refresh_cookies, unset_jwt_cookies)
from models import db, User

user_bp = Blueprint("user_bp", __name__)


@user_bp.route("/register", methods=["POST"])
def register_user():
    data = request.get_json()

    if data is None:
        return jsonify({"error": "Invalid JSON data"}), 400

    existing_user = User.query.filter_by(email=data["email"]).first()
    if existing_user:
        return jsonify({"error": "User with this email already exists"}), 409

    new_user = User()
    new_user.email = data["email"]
    new_user.password = data["password"]

    try:
        db.session.add(new_user)
        db.session.commit()

        return (jsonify({"message": "User registered successfully", "user_id": str(new_user.id)}), 201,)

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "An error occurred while registering the user: " + str(e)}), 500


@user_bp.route("/login", methods=["POST"])
def login_user():
    data = request.get_json()

    if data is None:
        return jsonify({"error": "Invalid JSON data"}), 400

    user = User.query.filter_by(email=data["email"]).first()

    try:
        if user and user.check_password(data["password"]):
            access_token = create_access_token(identity=user.id)
            refresh_token = create_refresh_token(identity=user.id)

            response = jsonify(
                {"message": "Login successful", "access_token": access_token})
            set_access_cookies(response, access_token)
            set_refresh_cookies(response, refresh_token)
            return response

    except ValueError:
        return jsonify({"error": "Invalid password hash"}), 500

    return jsonify({"message": "Invalid credentials"}), 400


@user_bp.route("/me", methods=["GET"])
@jwt_required()
def user_info():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if user:
        return jsonify({
            "id": user.id,
            "email": user.email,
        }), 200

    return jsonify({"message": "User not found"}), 400


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
def logout_user():
    response = jsonify({"message": "Logout successful"})
    unset_jwt_cookies(response)
    return response


@user_bp.route("/auth/check", methods=["GET"])
@jwt_required()
def auth_check():
    return jsonify({"msg": "Authenticated"}), 200
