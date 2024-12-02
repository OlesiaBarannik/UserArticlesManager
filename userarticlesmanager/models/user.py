from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String
from werkzeug.security import generate_password_hash, check_password_hash
from userarticlesmanager.extensions import db
from typing import Optional


# Constants for roles
class UserRoles:
    ADMIN = "Admin"
    EDITOR = "Editor"
    VIEWER = "Viewer"


# Constants for permissions
class Permissions:
    CREATE = "create"
    READ = "view"
    UPDATE = "update"
    DELETE = "delete"


class User(db.Model):  # type: ignore
    """User model representing a user in the database."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(200), nullable=False)
    role: Mapped[str] = mapped_column(
        String(50), nullable=False, default=UserRoles.VIEWER
    )
    articles: Mapped[list["Article"]] = relationship("Article", back_populates="user")  # type: ignore

    def __init__(
        self, username: str, password: str, role: str = UserRoles.VIEWER
    ) -> None:
        self.username = username
        self.password = password  # Uses setter to hash the password
        self.role = role

    @property
    def password(self) -> str:
        return self.password_hash

    @password.setter
    def password(self, raw_password: str) -> None:
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password: str) -> bool:
        return check_password_hash(self.password_hash, raw_password)

    def has_permission(
        self, permission: str, article_user_id: Optional[int] = None
    ) -> bool:
        """Check if the user has permission for a specific action."""
        if self.role == UserRoles.ADMIN:
            return True
        if self.role == UserRoles.EDITOR:
            return permission in [Permissions.READ, Permissions.UPDATE]
        if self.role == UserRoles.VIEWER:
            if permission == Permissions.READ:
                return True
            if permission == Permissions.CREATE:
                return article_user_id is None or article_user_id == self.id
            if permission in [Permissions.UPDATE, Permissions.DELETE]:
                return article_user_id == self.id
        return False

    def to_dict(self) -> dict[str, str]:
        return {
            "id": str(self.id),  # Convert id to string
            "username": self.username,
            "role": self.role,
        }
