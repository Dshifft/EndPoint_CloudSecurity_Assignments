from fastapi.testclient import TestClient

from main import voting_app
from utils.data_types import AdminJWTPayload
from utils.security import generate_admin_jwt


client = TestClient(voting_app)


def register_admin(admin_email: str) -> None:
    """Register an administrator used by tests that need an admin token."""
    response = client.post(
        "/admin/register",
        json={"name": "Admin Test", "email": admin_email, "password": "Password123!"},
    )
    assert response.status_code == 201


def admin_headers(admin_email: str) -> dict[str, str]:
    """Create a valid administrator header without sending an MFA email."""
    token = generate_admin_jwt(AdminJWTPayload(email=admin_email))
    return {"Authorization": f"Bearer {token}"}


def test_read_main() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the voting app!"}


def test_user_registration_and_login() -> None:
    user_name = "Voter Test"
    user_email = "voter_test@example.com"
    user_password = "Password123!"
    register_response = client.post(
        "/user/register",
        json={"name": user_name, "email": user_email, "password": user_password},
    )
    assert register_response.status_code == 201

    login_response = client.post("/user/login", json={"email": user_email, "password": user_password})
    assert login_response.status_code == 200
    assert login_response.json()["token"]


def test_admin_registration() -> None:
    admin_email = "admin_registration@example.com"
    register_admin(admin_email)


def test_candidate_registration_and_listing() -> None:
    candidate_admin_email = "candidate_admin@example.com"
    candidate_name = "Candidate Test"
    candidate_email = "candidate_test@example.com"
    register_admin(candidate_admin_email)

    register_response = client.post(
        "/admin/candidate",
        json={"name": candidate_name, "email": candidate_email},
        headers=admin_headers(candidate_admin_email),
    )
    assert register_response.status_code == 201

    list_response = client.get("/admin/candidate")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1


def test_vote_registration() -> None:
    vote_admin_email = "vote_admin@example.com"
    vote_candidate_name = "Candidate Vote"
    vote_candidate_email = "candidate_vote@example.com"
    register_admin(vote_admin_email)
    candidate_response = client.post(
        "/admin/candidate",
        json={"name": vote_candidate_name, "email": vote_candidate_email},
        headers=admin_headers(vote_admin_email),
    )
    assert candidate_response.status_code == 201

    user_name = "Voter Vote"
    user_email = "voter_vote@example.com"
    user_password = "Password123!"
    assert client.post(
        "/user/register",
        json={"name": user_name, "email": user_email, "password": user_password},
    ).status_code == 201
    user_login_response = client.post("/user/login", json={"email": user_email, "password": user_password})
    assert user_login_response.status_code == 200

    vote_response = client.post(
        "/user/vote",
        json={"candidate_id": candidate_response.json()["candidate_id"]},
        headers={"Authorization": f"Bearer {user_login_response.json()['token']}"},
    )
    assert vote_response.status_code == 201
