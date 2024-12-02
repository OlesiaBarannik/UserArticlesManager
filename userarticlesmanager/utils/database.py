from userarticlesmanager.models.user import User, UserRoles
from userarticlesmanager.models.article import Article
from userarticlesmanager.extensions import db


def create_sample_data() -> None:
    """Function to populate the database with sample data."""

    # Create users with different roles
    admin = User(username="admin", password="adminpass", role=UserRoles.ADMIN)
    editor = User(username="editor", password="editorpass", role=UserRoles.EDITOR)
    viewer = User(username="viewer", password="viewerpass", role=UserRoles.VIEWER)

    # Add users to session
    db.session.add(admin)
    db.session.add(editor)
    db.session.add(viewer)

    # Commit users to the database so they get an ID
    db.session.commit()

    # Create articles to populate
    article1 = Article(
        title="Article 1", content="Content of Article 1", user_id=admin.id
    )
    article2 = Article(
        title="Article 2", content="Content of Article 2", user_id=editor.id
    )
    article3 = Article(
        title="Article 3", content="Content of Article 3", user_id=viewer.id
    )

    # Add articles to session
    db.session.add(article1)
    db.session.add(article2)
    db.session.add(article3)

    # Commit changes to the database
    db.session.commit()

    print("Sample data created successfully!")
