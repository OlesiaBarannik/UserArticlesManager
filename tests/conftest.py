import pytest
from flask import Flask
from flask.testing import FlaskClient
from userarticlesmanager.extensions import create_app, db
from userarticlesmanager.routes import register_routes
from userarticlesmanager.models.user import User, UserRoles
from userarticlesmanager.models.article import Article
from typing import Generator


@pytest.fixture(scope="session")
def app() -> Generator[Flask, None, None]:
    """Create a test Flask app for the session."""
    from userarticlesmanager.test_config import TestConfig  # Import test configuration

    app = create_app(TestConfig)  # type: ignore
    app.config.update({"TESTING": True})

    with app.app_context():
        register_routes(app)
        db.create_all()

    yield app

    with app.app_context():
        db.drop_all()


@pytest.fixture(scope="function", autouse=True)
def prepare_database(app: Flask) -> None:
    """Reset database before each test."""
    with app.app_context():
        db.session.query(Article).delete()
        db.session.query(User).delete()
        db.session.commit()

        # Add a test user
        test_user = User(
            username="test_user", password="test_password", role=UserRoles.VIEWER
        )
        db.session.add(test_user)
        db.session.commit()


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    """Create a test Flask client."""
    return app.test_client()


@pytest.fixture
def get_access_token(client: FlaskClient, app: Flask) -> callable:  # type: ignore
    """Retrieve an access token for testing."""

    def _get_access_token(username: str, password: str) -> str:
        with app.app_context():
            if not User.query.filter_by(username=username).first():
                user = User(username=username, password=password, role=UserRoles.ADMIN)
                db.session.add(user)
                db.session.commit()

        response = client.post(
            "/api/login", json={"username": username, "password": password}
        )
        return response.get_json()["access_token"]

    return _get_access_token
