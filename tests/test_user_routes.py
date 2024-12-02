from userarticlesmanager.models.user import User, UserRoles
from userarticlesmanager.extensions import db


def test_login_success(client) -> None:
    """Test successful login."""
    response = client.post(
        "/api/login", json={"username": "test_user", "password": "test_password"}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert "access_token" in data
    assert data["message"] == "Login successful"


def test_list_users_admin(client, app, get_access_token) -> None:
    """Test getting a list of users as an admin."""
    with app.app_context():
        admin_user = User(
            username="admin_user", password="admin_password", role=UserRoles.ADMIN
        )
        db.session.add(admin_user)
        db.session.commit()

    access_token = get_access_token("admin_user", "admin_password")

    response = client.get(
        "/api/users", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)


def test_list_users_non_admin(client, get_access_token) -> None:
    """Test that non-admin cannot access the user list."""
    access_token = get_access_token("test_user", "test_password")

    response = client.get(
        "/api/users", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 403
    data = response.get_json()
    assert data["message"] == "Access denied"


def test_update_user_admin(client, app, get_access_token) -> None:
    """Test updating a user by admin."""
    with app.app_context():
        admin_user = User(
            username="admin_user", password="admin_password", role=UserRoles.ADMIN
        )
        regular_user = User(
            username="regular_user", password="regular_password", role=UserRoles.VIEWER
        )
        db.session.add_all([admin_user, regular_user])
        db.session.commit()
        regular_user_id = regular_user.id

    access_token = get_access_token("admin_user", "admin_password")

    response = client.patch(
        f"/api/users/{regular_user_id}",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"username": "updated_user", "role": UserRoles.EDITOR},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["user"]["username"] == "updated_user"
    assert data["user"]["role"] == UserRoles.EDITOR


def test_delete_user_admin(client, app, get_access_token) -> None:
    """Test deleting a user by admin."""
    with app.app_context():
        admin_user = User(
            username="admin_user", password="admin_password", role=UserRoles.ADMIN
        )
        regular_user = User(
            username="regular_user", password="regular_password", role=UserRoles.VIEWER
        )
        db.session.add_all([admin_user, regular_user])
        db.session.commit()
        regular_user_id = regular_user.id

    access_token = get_access_token("admin_user", "admin_password")

    response = client.delete(
        f"/api/users/{regular_user_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["message"] == "User deleted successfully"


def test_search_users(client, app, get_access_token) -> None:
    """Test searching for users by admin."""
    with app.app_context():
        admin_user = User(
            username="admin_user", password="admin_password", role=UserRoles.ADMIN
        )
        user1 = User(
            username="search_user1", password="password", role=UserRoles.VIEWER
        )
        user2 = User(
            username="search_user2", password="password", role=UserRoles.VIEWER
        )
        db.session.add_all([admin_user, user1, user2])
        db.session.commit()

    access_token = get_access_token("admin_user", "admin_password")

    response = client.get(
        "/api/users/search?username=search",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2
    assert data[0]["username"] == "search_user1"
    assert data[1]["username"] == "search_user2"


def test_login_invalid_password(client) -> None:
    """Test login with invalid password."""
    response = client.post(
        "/api/login", json={"username": "test_user", "password": "wrong_password"}
    )
    assert response.status_code == 401
    data = response.get_json()
    assert data["message"] == "Invalid credentials"


def test_search_users_no_results(client, app, get_access_token) -> None:
    """Test searching for users with no matching results."""
    with app.app_context():
        admin_user = User(
            username="admin_user", password="admin_password", role=UserRoles.ADMIN
        )
        db.session.add(admin_user)
        db.session.commit()

    access_token = get_access_token("admin_user", "admin_password")

    response = client.get(
        "/api/users/search?username=nonexistent",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 404
    data = response.get_json()
    assert data["message"] == "No users found"


def test_update_user_non_admin(client, app, get_access_token) -> None:
    """Test updating a user as non-admin."""
    with app.app_context():
        viewer_user = User(
            username="viewer_user", password="viewer_password", role=UserRoles.VIEWER
        )
        regular_user = User(
            username="regular_user", password="regular_password", role=UserRoles.VIEWER
        )
        db.session.add_all([viewer_user, regular_user])
        db.session.commit()
        regular_user_id = regular_user.id

    access_token = get_access_token("viewer_user", "viewer_password")

    response = client.patch(
        f"/api/users/{regular_user_id}",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"username": "unauthorized_update", "role": UserRoles.EDITOR},
    )
    assert response.status_code == 403
    data = response.get_json()
    assert data["message"] == "Access denied"


def test_delete_user_non_admin(client, app, get_access_token) -> None:
    """Test deleting a user as non-admin."""
    with app.app_context():
        viewer_user = User(
            username="viewer_user", password="viewer_password", role=UserRoles.VIEWER
        )
        regular_user = User(
            username="regular_user", password="regular_password", role=UserRoles.VIEWER
        )
        db.session.add_all([viewer_user, regular_user])
        db.session.commit()
        regular_user_id = regular_user.id

    access_token = get_access_token("viewer_user", "viewer_password")

    response = client.delete(
        f"/api/users/{regular_user_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 403
    data = response.get_json()
    assert data["message"] == "Access denied"


def test_delete_nonexistent_user(client, get_access_token) -> None:
    """Test deleting a nonexistent user."""
    access_token = get_access_token("admin_user", "admin_password")

    response = client.delete(
        "/api/users/9999",  # Nonexistent user ID
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 404
    data = response.get_json()
    assert data["message"] == "User not found"


def test_search_nonexistent_user(client, app, get_access_token) -> None:
    """Test searching for a nonexistent user."""
    with app.app_context():
        admin_user = User(username="admin_user", password="admin_password", role=UserRoles.ADMIN)
        db.session.add(admin_user)
        db.session.commit()

    access_token = get_access_token("admin_user", "admin_password")

    response = client.get(
        "/api/users/search?username=doesnotexist",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 404
    data = response.get_json()
    assert data["message"] == "No users found"


def test_update_nonexistent_user(client, get_access_token) -> None:
    """Test updating a nonexistent user."""
    access_token = get_access_token("admin_user", "admin_password")

    response = client.patch(
        "/api/users/9999",  # Nonexistent user ID
        headers={"Authorization": f"Bearer {access_token}"},
        json={"username": "updated_user", "role": UserRoles.EDITOR},
    )
    assert response.status_code == 404
    data = response.get_json()
    assert data["message"] == "User not found"
