import pytest

from tests.helpers import login_user, register_user


@pytest.mark.asyncio
async def test_create_task_happy_path(owner_client, owner_project_id):
    response = await owner_client.post(
        f"/projects/{owner_project_id}/tasks",
        json={
            "title": "Implement API",
            "description": "Create endpoints",
            "assignee_email": "owner@example.com",
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "todo"


@pytest.mark.asyncio
async def test_create_task_validation_error_for_empty_title(owner_client, owner_project_id):
    response = await owner_client.post(
        f"/projects/{owner_project_id}/tasks",
        json={"title": "", "description": "desc", "assignee_email": "owner@example.com"},
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_task_assignee_not_in_project_returns_404(test_client):
    await register_user(test_client, "Owner", "owner4@example.com")
    await login_user(test_client, "owner4@example.com")
    project_id = (await test_client.post("/projects", json={"name": "Tasks"})).json()["id"]

    await register_user(test_client, "Alien", "alien@example.com")
    response = await test_client.post(
        f"/projects/{project_id}/tasks",
        json={"title": "Task", "description": "Desc", "assignee_email": "alien@example.com"},
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_all_tasks_requires_project_membership(test_client, owner_project_id):
    await register_user(test_client, "Outsider", "outsider2@example.com")
    await login_user(test_client, "outsider2@example.com")

    response = await test_client.get(f"/projects/{owner_project_id}/tasks")

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_single_task_happy_path(owner_client, owner_project_id, owner_task_id):
    response = await owner_client.get(f"/projects/{owner_project_id}/tasks/{owner_task_id}")

    assert response.status_code == 200
    assert response.json()["id"] == owner_task_id


@pytest.mark.asyncio
async def test_update_task_edge_case_only_status_change(owner_client, owner_project_id, owner_task_id):
    response = await owner_client.patch(
        f"/projects/{owner_project_id}/tasks/{owner_task_id}",
        json={"status": "done"},
    )

    assert response.status_code == 200
    assert response.json() == {"success": True}


@pytest.mark.asyncio
async def test_update_task_invalid_status_returns_422(owner_client, owner_project_id, owner_task_id):
    response = await owner_client.patch(
        f"/projects/{owner_project_id}/tasks/{owner_task_id}",
        json={"status": "invalid"},
    )

    assert response.status_code == 422

@pytest.mark.asyncio
async def test_member_can_only_update_task_status_not_other_fields(test_client):
    await register_user(test_client, "Owner", "owner_tasks_member@example.com")
    await login_user(test_client, "owner_tasks_member@example.com")
    project_id = (await test_client.post("/projects", json={"name": "Team Tasks"})).json()["id"]
    await register_user(test_client, "Member", "member_tasks_member@example.com")
    await test_client.post(
        f"/projects/{project_id}/members", json={"email": "member_tasks_member@example.com"}
    )
    task_id = (
        await test_client.post(
            f"/projects/{project_id}/tasks",
            json={
                "title": "Initial",
                "description": "Initial description",
                "assignee_email": "member_tasks_member@example.com",
            },
        )
    ).json()["id"]

    await test_client.post("/users/auth/logout")
    await login_user(test_client, "member_tasks_member@example.com")
    forbidden = await test_client.patch(
        f"/projects/{project_id}/tasks/{task_id}",
        json={"title": "Cannot change title"},
    )
    allowed = await test_client.patch(
        f"/projects/{project_id}/tasks/{task_id}",
        json={"status": "in_progress"},
    )

    assert forbidden.status_code == 403
    assert allowed.status_code == 200


@pytest.mark.asyncio
async def test_owner_can_change_task_assignee_to_existing_member(test_client):
    await register_user(test_client, "Owner", "owner_assign@example.com")
    await login_user(test_client, "owner_assign@example.com")
    project_id = (await test_client.post("/projects", json={"name": "Assign Project"})).json()["id"]
    await register_user(test_client, "Member", "member_assign@example.com")
    await test_client.post(f"/projects/{project_id}/members", json={"email": "member_assign@example.com"})
    task_id = (
        await test_client.post(
            f"/projects/{project_id}/tasks",
            json={
                "title": "Task",
                "description": "Desc",
                "assignee_email": "owner_assign@example.com",
            },
        )
    ).json()["id"]

    update = await test_client.patch(
        f"/projects/{project_id}/tasks/{task_id}",
        json={"assignee_email": "member_assign@example.com"},
    )
    task = await test_client.get(f"/projects/{project_id}/tasks/{task_id}")

    assert update.status_code == 200
    assert task.status_code == 200
    assert task.json()["assignee_email"] == "member_assign@example.com"


@pytest.mark.asyncio
async def test_owner_change_task_assignee_to_non_member_returns_404(test_client):
    await register_user(test_client, "Owner", "owner_assign2@example.com")
    await login_user(test_client, "owner_assign2@example.com")
    project_id = (await test_client.post("/projects", json={"name": "Assign2 Project"})).json()["id"]
    task_id = (
        await test_client.post(
            f"/projects/{project_id}/tasks",
            json={
                "title": "Task",
                "description": "Desc",
                "assignee_email": "owner_assign2@example.com",
            },
        )
    ).json()["id"]
    await register_user(test_client, "Alien", "alien_assign2@example.com")

    response = await test_client.patch(
        f"/projects/{project_id}/tasks/{task_id}",
        json={"assignee_email": "alien_assign2@example.com"},
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_task_from_wrong_project_returns_404(owner_client, owner_project_id, owner_task_id):
    second_project_id = (await owner_client.post("/projects", json={"name": "Second Project"})).json()["id"]
    response = await owner_client.get(f"/projects/{second_project_id}/tasks/{owner_task_id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_task_happy_path(owner_client, owner_project_id, owner_task_id):
    delete_response = await owner_client.delete(f"/projects/{owner_project_id}/tasks/{owner_task_id}")
    get_response = await owner_client.get(f"/projects/{owner_project_id}/tasks/{owner_task_id}")

    assert delete_response.status_code == 200
    assert get_response.status_code == 404
