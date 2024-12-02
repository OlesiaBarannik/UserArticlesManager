from userarticlesmanager.models.user import User
from userarticlesmanager.extensions import db


def create_user(username: str, password: str, role: str = "Viewer") -> User:
    """Create a new user in the database."""

    # Check if the user already exists
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        raise ValueError("A user with this username already exists.")

    # Create a new user
    user = User(username=username, password=password, role=role)

    # Add to the database
    db.session.add(user)
    db.session.commit()

    return user
