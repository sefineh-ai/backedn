"""
User endpoint tests aligned with current API structure.
"""
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def signup_user(full_name: str, email: str, password: str = "Password1!", role: str = "applicant") -> str:
    payload = {
        "full_name": full_name,
        "email": email,
        "password": password,
        "role": role,
    }
    response = client.post("/api/v1/users/signup", json=payload)
    assert response.status_code == 201
    body = response.json()
    assert body["success"] is True
    return body["object"]["id"]


class TestUserEndpoints:
    def test_signup_user(self):
        user_id = signup_user("Test User", "test@example.com")
        assert user_id

    def test_get_user(self):
        user_id = signup_user("Get User", "get@example.com")
        response = client.get(f"/api/v1/users/{user_id}")
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["object"]["email"] == "get@example.com"

    def test_update_user(self):
        user_id = signup_user("Update User", "update@example.com")
        update_data = {"full_name": "Updated User"}
        response = client.put(f"/api/v1/users/{user_id}", json=update_data)
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["object"]["full_name"] == "Updated User"

    def test_delete_user(self):
        user_id = signup_user("Delete User", "delete@example.com")
        response = client.delete(f"/api/v1/users/{user_id}")
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        # Ensure subsequent get shows not found
        get_response = client.get(f"/api/v1/users/{user_id}")
        get_body = get_response.json()
        assert get_body["success"] is False