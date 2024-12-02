from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask.cli import with_appcontext
from flasgger import Swagger  # type: ignore
from flask_cors import CORS  # type: ignore
import click
import os

# Initialization of components
db = SQLAlchemy()
jwt = JWTManager()


def create_app(config_class: str = "userarticlesmanager.config.Config") -> Flask:
    """Function to create a Flask application instance."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize components
    db.init_app(app)
    jwt.init_app(app)

    CORS(app)

    Swagger(app, template_file="swagger_config.yml")

    app.cli.add_command(create_sample_data_command)

    return app


@click.command(name="create-sample-data")
@with_appcontext
def create_sample_data_command() -> None:
    """Command to create sample data in the database."""
    from userarticlesmanager.utils.database import create_sample_data

    create_sample_data()
