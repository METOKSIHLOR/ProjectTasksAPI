import pytest

from tests.helpers import login_user, register_user


@pytest.mark.asyncio
async def test_create_project_happy_path(owner_client):
    response = await owner_client.post("/projects", json={"name": "Backend API"})

    assert response.status_code == 200
    assert response.json()["name"] == "Backend API"


@pytest.mark.asyncio
async def test_create_project_validation_error_for_short_name(owner_client):
    response = await owner_client.post("/projects", json={"name": "ab"})

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_all_user_projects_returns_created_projects(owner_client):
    await owner_client.post("/projects", json={"name": "Project A"})
    await owner_client.post("/projects", json={"name": "Project B"})

    response = await owner_client.get("/projects")

    assert response.status_code == 200
    names = [p["name"] for p in response.json()]
    assert "Project A" in names and "Project B" in names


@pytest.mark.asyncio
async def test_get_project_details_forbidden_for_non_member(test_client, owner_project_id):
    await register_user(test_client, "Outsider", "outsider@example.com")
    await login_user(test_client, "outsider@example.com")

    response = await test_client.get(f"/projects/{owner_project_id}")

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_update_project_name_happy_path(owner_client, owner_project_id):
    response = await owner_client.patch(
        f"/projects/{owner_project_id}",
        json={"name": "Renamed Project"},
    )

    assert response.status_code == 200
    assert response.json() == {"success": True}


@pytest.mark.asyncio
async def test_add_member_and_member_can_view_project(test_client, owner_project_id):
    # owner session
    await register_user(test_client, "Owner", "owner2@example.com")
    await login_user(test_client, "owner2@example.com")
    create_project = await test_client.post("/projects", json={"name": "Team project"})
    project_id = create_project.json()["id"]

    await register_user(test_client, "Member", "member2@example.com")
    add_member = await test_client.post(
        f"/projects/{project_id}/members", json={"email": "member2@example.com"}
    )

    assert add_member.status_code == 200

    # member session
    await test_client.post("/users/auth/logout")
    await login_user(test_client, "member2@example.com")
    project_details = await test_client.get(f"/projects/{project_id}")

    assert project_details.status_code == 200
    assert project_details.json()["name"] == "Team project"


@pytest.mark.asyncio
async def test_add_member_duplicate_returns_409(test_client):
    await register_user(test_client, "Owner", "owner3@example.com")
    await login_user(test_client, "owner3@example.com")
    project_id = (await test_client.post("/projects", json={"name": "One"})).json()["id"]

    await register_user(test_client, "Member", "member3@example.com")
    await test_client.post(f"/projects/{project_id}/members", json={"email": "member3@example.com"})
    second_add = await test_client.post(
        f"/projects/{project_id}/members", json={"email": "member3@example.com"}
    )

    assert second_add.status_code == 409


@pytest.mark.asyncio
async def test_remove_member_self_delete_forbidden(owner_client, owner_project_id):
    response = await owner_client.request(
        "DELETE",
        f"/projects/{owner_project_id}/members",
        json={"email": "owner@example.com"},
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_delete_project_happy_path(owner_client, owner_project_id):
    delete_response = await owner_client.delete(f"/projects/{owner_project_id}")
    read_response = await owner_client.get(f"/projects/{owner_project_id}")

    assert delete_response.status_code == 200
    assert delete_response.json() == {"success": True}
    assert read_response.status_code == 404
