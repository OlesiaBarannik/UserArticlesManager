from userarticlesmanager.extensions import create_app
from userarticlesmanager.extensions import db
from userarticlesmanager.models.user import User
from userarticlesmanager.models.article import Article
from userarticlesmanager.routes import register_routes
from typing import Any

app = create_app()
register_routes(app)


@app.shell_context_processor
def make_shell_context() -> dict[str, Any]:
    """Shell context for Flask CLI, providing access to db, User, and Article models."""
    return {"db": db, "User": User, "Article": Article}
