from flask import Blueprint, request, jsonify, Response
from flask_jwt_extended import jwt_required, get_jwt_identity
from userarticlesmanager.models.user import User, Permissions
from userarticlesmanager.models.article import Article
from userarticlesmanager.extensions import db
from flasgger import swag_from  # type: ignore
from typing import Any, Optional


article_routes = Blueprint("article_routes", __name__)


@article_routes.route("/articles", methods=["POST"])
@jwt_required()
@swag_from("../swagger_config.yml", endpoint="articles", methods=["POST"])
def create_article() -> Response:
    """Create a new article (Admin or Viewer)."""
    user_id = get_jwt_identity()
    current_user = User.query.get(user_id)

    data = request.json
    if not data:
        response = jsonify({"message": "No input data provided"})
        response.status_code = 400
        return response

    title = data.get("title")
    content = data.get("content")
    target_user_id = data.get("user_id", user_id)  # Default to self

    if not title or not content:
        response = jsonify({"message": "Title and content are required"})
        response.status_code = 400
        return response

    # Check permission to create the article
    if not current_user.has_permission(
        Permissions.CREATE, article_user_id=target_user_id
    ):
        response = jsonify({"message": "Access denied"})
        response.status_code = 403
        return response

    # Create article
    article = Article(title=title, content=content, user_id=target_user_id)
    db.session.add(article)
    db.session.commit()
    response = jsonify(article.to_dict())
    response.status_code = 201
    return response


@article_routes.route("/articles", methods=["GET"])
@article_routes.route("/articles/<int:article_id>", methods=["GET"])
@jwt_required()
@swag_from("../swagger_config.yml", endpoint="articles", methods=["GET"])
def get_articles(article_id: Optional[int] = None) -> Response:
    """Get all articles or one article by ID. Available for all roles (authentication required)."""
    user_id = get_jwt_identity()
    current_user = User.query.get(user_id)

    if article_id:
        article = Article.query.get(article_id)
        if article:
            if article.user_id == user_id or current_user.has_permission(
                Permissions.READ
            ):
                return jsonify(article.to_dict())
            else:
                response = jsonify({"message": "Access denied"})
                response.status_code = 403
                return response
        else:
            response = jsonify({"message": "Article not found"})
            response.status_code = 404
            return response
    else:
        articles = Article.query.all()
        return jsonify([article.to_dict() for article in articles])


@article_routes.route("/articles/search", methods=["GET"])
@jwt_required()
@swag_from("../swagger_config.yml", endpoint="articles_search", methods=["GET"])
def search_articles() -> Response:
    """Search articles by title. Available for all roles (authentication required)."""
    title = request.args.get("title", "").lower()
    if not title:
        response = jsonify({"message": "Title parameter is required"})
        response.status_code = 400
        return response

    articles = Article.query.filter(Article.title.ilike(f"%{title}%")).all()

    if not articles:
        response = jsonify({"message": "No articles found"})
        response.status_code = 404
        return response

    return jsonify([article.to_dict() for article in articles])


@article_routes.route("/articles/<int:article_id>", methods=["PATCH"])
@jwt_required()
@swag_from("../swagger_config.yml", endpoint="articles_update", methods=["PATCH"])
def update_articles(article_id: int) -> Response:
    """Update article. Viewer can update only their articles, Editor and Admin can update any."""
    user_id = get_jwt_identity()
    current_user = User.query.get(user_id)

    article = Article.query.get(article_id)
    if not article:
        response = jsonify({"message": "Article not found"})
        response.status_code = 404
        return response

    if not current_user.has_permission(
        Permissions.UPDATE, article_user_id=article.user_id
    ):
        response = jsonify({"message": "Access denied"})
        response.status_code = 403
        return response

    data = request.json
    if not data:
        response = jsonify({"message": "No input data provided"})
        response.status_code = 400
        return response

    title = data.get("title")
    content = data.get("content")

    if title is not None:
        article.title = title
    if content is not None:
        article.content = content

    db.session.commit()
    return jsonify(article.to_dict())


@article_routes.route("/articles/<int:article_id>", methods=["DELETE"])
@jwt_required()
@swag_from("../swagger_config.yml", endpoint="articles_delete", methods=["DELETE"])
def delete_article(article_id: int) -> Response:
    """Delete article. Viewer can delete only their articles, Admin can delete any, Editor cannot delete."""
    user_id = get_jwt_identity()
    current_user = User.query.get(user_id)

    article = Article.query.get(article_id)
    if not article:
        response = jsonify({"message": "Article not found"})
        response.status_code = 404
        return response

    if not current_user.has_permission(
        Permissions.DELETE, article_user_id=article.user_id
    ):
        response = jsonify({"message": "Access denied"})
        response.status_code = 403
        return response

    db.session.delete(article)
    db.session.commit()
    response = jsonify({"message": "Article deleted successfully"})
    response.status_code = 200
    return response
