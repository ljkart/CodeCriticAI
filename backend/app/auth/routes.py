"""Module to list all authourization routes."""

from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import jwt_required
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
)
from app import db
from app.models import user

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    """Endpoint used to register the user at first time"""
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    if user.User.query.filter_by(username=username).first():
        return (
            jsonify({"error": f"Username `{username}` already exists"}),
            409,
        )

    hashed_pw = generate_password_hash(password)
    db_user = user.User(username=username, password_hash=hashed_pw)
    db.session.add(db_user)
    db.session.commit()
    return (
        jsonify(
            {
                "message": "Registration Successful",
                "user": {"username": db_user.username},
            }
        ),
        201,
    )


@auth_bp.route("/login", methods=["POST"])
def login():
    """Endpoint to allow user to login"""
    data = request.get_json()
    db_user = user.User.query.filter_by(username=data.get("username")).first()
    if not db_user or not check_password_hash(
        db_user.password_hash, data.get("password")
    ):
        return jsonify({"message": "Invalid credentials"}), 401
    token = create_access_token(identity=str(db_user.id))
    refresh_token = create_refresh_token(identity=str(db_user.id))
    return (
        jsonify(
            {
                "user": {"id": db_user.id, "name": db_user.username},
                "token": token,
                "refresh_token": refresh_token,
            }
        ),
        200,
    )


@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh_login():
    """Entopoint used to refresh the token so that user dont have re-login"""
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return jsonify({"token": access_token})
