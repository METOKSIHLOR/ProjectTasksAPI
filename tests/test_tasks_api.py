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
        json={
            "title": "",
            "description": "",
            "status": "done",
            "assignee_email": "",
        },
    )

    assert response.status_code == 200
    assert response.json() == {"success": True}


@pytest.mark.asyncio
async def test_update_task_invalid_status_returns_422(owner_client, owner_project_id, owner_task_id):
    response = await owner_client.patch(
        f"/projects/{owner_project_id}/tasks/{owner_task_id}",
        json={
            "title": "",
            "description": "",
            "status": "invalid",
            "assignee_email": "",
        },
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_delete_task_happy_path(owner_client, owner_project_id, owner_task_id):
    delete_response = await owner_client.delete(f"/projects/{owner_project_id}/tasks/{owner_task_id}")
    get_response = await owner_client.get(f"/projects/{owner_project_id}/tasks/{owner_task_id}")

    assert delete_response.status_code == 200
    assert get_response.status_code == 404
