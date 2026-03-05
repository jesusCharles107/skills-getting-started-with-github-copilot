"""Tests for the FastAPI activities endpoints using Arrange-Act-Assert (AAA).
"""


def test_get_activities_returns_dict(client):
    # Arrange: default state provided by the app

    # Act
    resp = client.get("/activities")

    # Assert
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]


def test_signup_success(client):
    # Arrange
    activity = "Chess Club"
    email = "newstudent@example.com"
    assert email not in client.get("/activities").json()[activity]["participants"]

    # Act
    resp = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert resp.status_code == 200
    assert email in client.get("/activities").json()[activity]["participants"]
    assert "Signed up" in resp.json().get("message", "")


def test_signup_already_registered(client):
    # Arrange: use an existing participant from the seed data
    activity = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    resp = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert resp.status_code == 400
    assert "already signed up" in resp.json().get("detail", "").lower()


def test_signup_missing_activity(client):
    # Arrange
    activity = "Nonexistent Club"
    email = "someone@example.com"

    # Act
    resp = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert resp.status_code == 404


def test_unregister_success(client):
    # Arrange
    activity = "Chess Club"
    email = "temp@mergington.edu"

    # Sign up first
    r1 = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert r1.status_code == 200

    # Act
    r2 = client.delete(f"/activities/{activity}/unregister", params={"email": email})

    # Assert
    assert r2.status_code == 200
    assert email not in client.get("/activities").json()[activity]["participants"]


def test_unregister_not_registered(client):
    # Arrange
    activity = "Chess Club"
    email = "notregistered@example.com"

    # Act
    resp = client.delete(f"/activities/{activity}/unregister", params={"email": email})

    # Assert
    assert resp.status_code == 400


def test_root_redirects_to_static(client):
    # Act
    resp = client.get("/", follow_redirects=False)

    # Assert
    assert resp.status_code in (302, 307)
    assert "/static/index.html" in resp.headers.get("location", "")
