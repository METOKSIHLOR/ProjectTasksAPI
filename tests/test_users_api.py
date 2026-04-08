import pytest

from tests.helpers import login_user, register_user


@pytest.mark.asyncio
async def test_user_registration_happy_path(test_client):
    response = await register_user(test_client, "Anton", "anton@example.com")

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Anton"
    assert body["email"] == "anton@example.com"


@pytest.mark.asyncio
async def test_user_registration_duplicate_email_returns_409(test_client):
    await register_user(test_client, "Anton", "anton@example.com")

    response = await register_user(test_client, "Anton 2", "anton@example.com")

    assert response.status_code == 409
    assert response.json()["detail"] == "User email already in use"


@pytest.mark.asyncio
async def test_user_registration_validation_error_for_short_name(test_client):
    response = await test_client.post(
        "/users/registration",
        json={"name": "ab", "email": "a@b.com", "password": "secret123"},
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_happy_path_sets_session_cookie(test_client):
    await register_user(test_client, "Anton", "anton@example.com")

    response = await login_user(test_client, "anton@example.com")

    assert response.status_code == 200
    assert response.json() == {"success": True}
    assert "session_id=" in response.headers["set-cookie"]


@pytest.mark.asyncio
async def test_login_with_wrong_password_returns_401(test_client):
    await register_user(test_client, "Anton", "anton@example.com")

    response = await login_user(test_client, "anton@example.com", password="wrong")

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


@pytest.mark.asyncio
async def test_get_me_requires_auth_cookie(test_client):
    response = await test_client.get("/users/me")

    assert response.status_code == 401
    assert response.json()["detail"] == "User not authorized"


@pytest.mark.asyncio
async def test_get_me_happy_path(test_client):
    await register_user(test_client, "Anton", "anton@example.com")
    await login_user(test_client, "anton@example.com")

    response = await test_client.get("/users/me")

    assert response.status_code == 200
    assert response.json()["email"] == "anton@example.com"


@pytest.mark.asyncio
async def test_logout_without_cookie_returns_401(test_client):
    response = await test_client.post("/users/auth/logout")

    assert response.status_code == 401
    assert response.json()["detail"] == "User not authorized"


@pytest.mark.asyncio
async def test_logout_invalidates_session_and_future_me_is_401(test_client):
    await register_user(test_client, "Anton", "anton@example.com")
    await login_user(test_client, "anton@example.com")

    logout_response = await test_client.post("/users/auth/logout")
    me_response = await test_client.get("/users/me")

    assert logout_response.status_code == 200
    assert logout_response.json() == {"success": True}
    assert me_response.status_code == 401
    assert me_response.json()["detail"] == "User not authorized"
    
@pytest.mark.asyncio
async def test_get_me_with_invalid_session_cookie_returns_401(test_client):
    test_client.cookies.set("session_id", "definitely-invalid-session")
    response = await test_client.get("/users/me")
    assert response.status_code == 401
    assert response.json()["detail"] == "User not authorized"


@pytest.mark.asyncio
async def test_login_with_unknown_email_returns_401(test_client):
    response = await login_user(test_client, "ghost@example.com")
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


@pytest.mark.asyncio
async def test_update_me_requires_auth_cookie(test_client):
    response = await test_client.patch("/users/me", json={"name": "New Name"})

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_me_validation_error_for_short_name(test_client):
    await register_user(test_client, "Anton", "anton@example.com")
    await login_user(test_client, "anton@example.com")

    response = await test_client.patch("/users/me", json={"name": "ab"})
    assert response.status_code == 422