from userarticlesmanager.routes.user_routes import user_routes
from userarticlesmanager.routes.article_routes import article_routes
from typing import Any


def register_routes(app) -> Any:
    """Register all routes."""
    app.register_blueprint(user_routes, url_prefix="/api")
    app.register_blueprint(article_routes, url_prefix="/api")
