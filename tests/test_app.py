from fastapi.testclient import TestClient

from src.app import app

client = TestClient(app)


def test_signup_for_activity_adds_participant():
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"
    client.delete(f"/activities/{activity_name}/participants/{email}")

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"

    activities = client.get("/activities").json()
    assert email in activities[activity_name]["participants"]


def test_signup_rejects_duplicate_participants():
    # Arrange
    activity_name = "Chess Club"
    email = "existing@mergington.edu"
    client.delete(f"/activities/{activity_name}/participants/{email}")
    client.post(f"/activities/{activity_name}/signup?email={email}")

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"].lower()


def test_unregister_participant_removes_email_from_activity():
    # Arrange
    activity_name = "Chess Club"
    email = "remove-me@mergington.edu"
    client.delete(f"/activities/{activity_name}/participants/{email}")
    client.post(f"/activities/{activity_name}/signup?email={email}")

    # Act
    response = client.delete(f"/activities/{activity_name}/participants/{email}")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from {activity_name}"

    activities = client.get("/activities").json()
    assert email not in activities[activity_name]["participants"]


def test_unregister_missing_participant_returns_404():
    # Arrange
    activity_name = "Chess Club"
    email = "ghost@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants/{email}")

    # Assert
    assert response.status_code == 404


def test_signup_rejects_full_activity():
    # Arrange
    activity_name = "Chess Club"
    full_email = "late@mergington.edu"
    activity = client.get("/activities").json()[activity_name]
    while len(activity["participants"]) < activity["max_participants"]:
        extra_email = f"student{len(activity['participants'])}@mergington.edu"
        client.post(f"/activities/{activity_name}/signup?email={extra_email}")
        activity = client.get("/activities").json()[activity_name]

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={full_email}")

    # Assert
    assert response.status_code == 400
    assert "activity is full" in response.json()["detail"].lower()
