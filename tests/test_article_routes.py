from userarticlesmanager.models.user import User, UserRoles
from userarticlesmanager.models.article import Article
from userarticlesmanager.extensions import db


def test_create_article_admin(client, get_access_token) -> None:
    """Test article creation by admin."""
    access_token = get_access_token("admin_user", "admin_password")

    response = client.post(
        "/api/articles",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "title": "Test Article",
            "content": "This is a test article.",
        },
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data["title"] == "Test Article"
    assert data["content"] == "This is a test article."


def test_get_articles_viewer(client, app, get_access_token) -> None:
    """Test getting articles as a viewer."""
    with app.app_context():
        viewer_user = User(
            username="viewer_user", password="viewer_password", role=UserRoles.VIEWER
        )
        article = Article(
            title="Viewer Article", content="Content for viewer.", user_id=1
        )
        db.session.add_all([viewer_user, article])
        db.session.commit()

    access_token = get_access_token("viewer_user", "viewer_password")

    response = client.get(
        "/api/articles", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1
    assert data[0]["title"] == "Viewer Article"


def test_update_article_editor(client, app, get_access_token) -> None:
    """Test updating an article by an editor."""
    with app.app_context():
        editor_user = User(
            username="editor_user", password="editor_password", role=UserRoles.EDITOR
        )
        article = Article(title="Old Title", content="Old Content", user_id=1)
        db.session.add_all([editor_user, article])
        db.session.commit()
        article_id = article.id

    access_token = get_access_token("editor_user", "editor_password")

    response = client.patch(
        f"/api/articles/{article_id}",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"title": "Updated Title", "content": "Updated Content"},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["title"] == "Updated Title"
    assert data["content"] == "Updated Content"


def test_delete_article_admin(client, app, get_access_token) -> None:
    """Test deleting an article by admin."""
    with app.app_context():
        admin_user = User(
            username="admin_user", password="admin_password", role=UserRoles.ADMIN
        )
        article = Article(title="Delete Me", content="Content to delete", user_id=1)
        db.session.add_all([admin_user, article])
        db.session.commit()
        article_id = article.id

    access_token = get_access_token("admin_user", "admin_password")

    response = client.delete(
        f"/api/articles/{article_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["message"] == "Article deleted successfully"

    with app.app_context():
        deleted_article = Article.query.get(article_id)
        assert deleted_article is None


def test_search_articles(client, app, get_access_token) -> None:
    """Test searching for articles."""
    with app.app_context():
        admin_user = User(
            username="admin_user", password="admin_password", role=UserRoles.ADMIN
        )
        article1 = Article(title="Searchable Article 1", content="Content 1", user_id=1)
        article2 = Article(title="Searchable Article 2", content="Content 2", user_id=1)
        db.session.add_all([admin_user, article1, article2])
        db.session.commit()

    access_token = get_access_token("admin_user", "admin_password")

    response = client.get(
        "/api/articles/search?title=Searchable",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2
    assert data[0]["title"] == "Searchable Article 1"
    assert data[1]["title"] == "Searchable Article 2"


def test_invalid_article_id(client, get_access_token) -> None:
    access_token = get_access_token("admin_user", "admin_password")

    response = client.get(
        "/api/articles/9999",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 404
    data = response.get_json()
    assert data["message"] == "Article not found"


def test_editor_cannot_delete_articles(client, app, get_access_token) -> None:
    with app.app_context():
        editor_user = User(
            username="editor_user", password="editor_password", role=UserRoles.EDITOR
        )
        article = Article(title="Undeletable Article", content="Protected", user_id=1)
        db.session.add_all([editor_user, article])
        db.session.commit()
        article_id = article.id

    access_token = get_access_token("editor_user", "editor_password")

    response = client.delete(
        f"/api/articles/{article_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 403
    data = response.get_json()
    assert data["message"] == "Access denied"


def test_missing_authorization(client) -> None:
    """Test accessing an endpoint without authorization header."""
    response = client.get("/api/articles")
    assert response.status_code == 401
    data = response.get_json()
    assert data["msg"] == "Missing Authorization Header"


def test_viewer_cannot_create_article_for_another_user(
    client, app, get_access_token
) -> None:
    """Test Viewer cannot create an article for another user."""
    with app.app_context():
        viewer_user = User(
            username="viewer_user", password="viewer_password", role=UserRoles.VIEWER
        )
        db.session.add(viewer_user)
        db.session.commit()

        # We check that the user received the correct ID
        viewer_user_id = viewer_user.id

    access_token = get_access_token("viewer_user", "viewer_password")

    # We are making a request to create an article for another user (ID = 9999)
    response = client.post(
        "/api/articles",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "title": "Viewer Restricted",
            "content": "Viewer cannot create for others.",
            "user_id": 9999,  # ID іншого користувача
        },
    )

    # Checking that the request is prohibited
    assert response.status_code == 403
    data = response.get_json()
    assert data["message"] == "Access denied"


def test_create_article_missing_data(client, get_access_token) -> None:
    """Test article creation with missing title or content."""
    access_token = get_access_token("admin_user", "admin_password")

    response = client.post(
        "/api/articles",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"title": "Incomplete Article"},
    )
    assert response.status_code == 400
    data = response.get_json()
    assert data["message"] == "Title and content are required"


def test_search_articles_no_results(client, get_access_token) -> None:
    """Test searching for articles with no matching results."""
    access_token = get_access_token("admin_user", "admin_password")

    response = client.get(
        "/api/articles/search?title=Nonexistent",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 404
    data = response.get_json()
    assert data["message"] == "No articles found"
