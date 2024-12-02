from flask import Blueprint, request, jsonify, Response
from userarticlesmanager.models.user import User, UserRoles, Permissions
from userarticlesmanager.models.article import Article
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from userarticlesmanager.extensions import db
from flasgger import swag_from  # type: ignore

user_routes = Blueprint("user_routes", __name__)


@user_routes.route("/login", methods=["POST"])
@swag_from("../../swagger_config.yml", endpoint="login", methods=["POST"])
def login() -> Response:
    """Login and generate access token."""
    data = request.json
    if not data:
        response = jsonify({"message": "No input data provided"})
        response.status_code = 400
        return response

    username = data.get("username")
    password = data.get("password")
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        access_token = create_access_token(identity=str(user.id))
        response = jsonify(
            {"message": "Login successful", "access_token": access_token}
        )
        response.status_code = 200
        return response

    response = jsonify({"message": "Invalid credentials"})
    response.status_code = 401
    return response


@user_routes.route("/users", methods=["GET"])
@jwt_required()
@swag_from("../../swagger_config.yml", endpoint="users_list", methods=["GET"])
def list_users() -> Response:
    """List all users (Admin only)."""
    user_id = get_jwt_identity()
    current_user = User.query.get(user_id)
    if current_user.role != UserRoles.ADMIN:
        response = jsonify({"message": "Access denied"})
        response.status_code = 403
        return response

    users = User.query.all()
    response = jsonify([user.to_dict() for user in users])
    response.status_code = 200
    return response


@user_routes.route("/users/<int:user_id>", methods=["GET"])
@jwt_required()
@swag_from("../../swagger_config.yml", endpoint="users_get", methods=["GET"])
def get_user(user_id: int) -> Response:
    """Get user details (Admin only)."""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    if current_user.role != UserRoles.ADMIN:
        response = jsonify({"message": "Access denied"})
        response.status_code = 403
        return response

    user = User.query.get(user_id)
    if not user:
        response = jsonify({"message": "User not found"})
        response.status_code = 404
        return response

    response = jsonify(user.to_dict())
    response.status_code = 200
    return response


@user_routes.route("/users/search", methods=["GET"])
@jwt_required()
@swag_from("../../swagger_config.yml", endpoint="users_search", methods=["GET"])
def search_users() -> Response:
    """Search users by username (Admin only)."""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    if current_user.role != UserRoles.ADMIN:
        response = jsonify({"message": "Access denied"})
        response.status_code = 403
        return response

    username = request.args.get("username", "").lower()

    users = User.query.filter(User.username.ilike(f"%{username}%")).all()

    if not users:
        response = jsonify({"message": "No users found"})
        response.status_code = 404
        return response

    response = jsonify([user.to_dict() for user in users])
    response.status_code = 200
    return response


@user_routes.route("/users/<int:user_id>", methods=["PATCH"])
@jwt_required()
@swag_from("../../swagger_config.yml", endpoint="users_update", methods=["PATCH"])
def update_user(user_id: int) -> Response:
    """Update a user's details (Admin only)."""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)

    if current_user.role != UserRoles.ADMIN:
        response = jsonify({"message": "Access denied"})
        response.status_code = 403
        return response

    user = User.query.get(user_id)
    if not user:
        response = jsonify({"message": "User not found"})
        response.status_code = 404
        return response

    data = request.json
    if not data:
        response = jsonify({"message": "No input data provided"})
        response.status_code = 400
        return response

    username = data.get("username")
    role = data.get("role")

    if username:
        user.username = username
    if role in [UserRoles.ADMIN, UserRoles.EDITOR, UserRoles.VIEWER]:
        user.role = role

    db.session.commit()

    response = jsonify({"message": "User updated successfully", "user": user.to_dict()})
    response.status_code = 200
    return response


@user_routes.route("/users/<int:user_id>", methods=["DELETE"])
@jwt_required()
@swag_from("../../swagger_config.yml", endpoint="users_delete", methods=["DELETE"])
def delete_user(user_id: int) -> Response:
    """Delete a user (Admin only)."""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)

    if current_user.role != UserRoles.ADMIN:
        response = jsonify({"message": "Access denied"})
        response.status_code = 403
        return response

    user = User.query.get(user_id)
    if not user:
        response = jsonify({"message": "User not found"})
        response.status_code = 404
        return response

    articles = Article.query.filter_by(user_id=user_id).all()
    for article in articles:
        db.session.delete(article)

    db.session.delete(user)
    db.session.commit()

    response = jsonify({"message": "User deleted successfully"})
    response.status_code = 200
    return response
