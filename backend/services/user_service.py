import re
from flask import jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    set_access_cookies,
    set_refresh_cookies)

from models import db, User


def register_user(email, password):
    existing_user = User.query.filter_by(email=email).first()

    if existing_user:
        return False, "User already exists"

    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if not re.fullmatch(email_regex, email):
        return False, "Invalid email format"
    new_user = User(email=email, password=password)

    try:
        db.session.add(new_user)
        db.session.commit()
        return True, None
    except Exception:
        db.session.rollback()
        return False, str("An error occurred while registering the user")


def login_user(email, password):
    user = User.query.filter_by(email=email).first()

    try:
        if user and user.check_password(password):
            access_token = create_access_token(identity=user.id)
            refresh_token = create_refresh_token(identity=user.id)

            response = jsonify({
                "message": "Login successful",
                "access_token": access_token
            })
            set_access_cookies(response, access_token)
            set_refresh_cookies(response, refresh_token)
            return True, response

        else:
            return False, "Invalid email or password"

    except Exception as e:
        return False, f"An error occurred while logging in: {e}"
