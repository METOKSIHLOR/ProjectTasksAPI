import pytest

from tests.helpers import login_user, register_user


@pytest.mark.asyncio
async def test_create_comment_happy_path(owner_client, owner_project_id, owner_task_id):
    response = await owner_client.post(
        f"/projects/{owner_project_id}/tasks/{owner_task_id}/comments",
        json={"text": "Looks good"},
    )

    assert response.status_code == 200
    assert response.json()["text"] == "Looks good"


@pytest.mark.asyncio
async def test_create_comment_validation_error_for_empty_text(owner_client, owner_project_id, owner_task_id):
    response = await owner_client.post(
        f"/projects/{owner_project_id}/tasks/{owner_task_id}/comments",
        json={"text": ""},
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_comments_happy_path(owner_client, owner_project_id, owner_task_id):
    await owner_client.post(
        f"/projects/{owner_project_id}/tasks/{owner_task_id}/comments",
        json={"text": "First"},
    )

    response = await owner_client.get(f"/projects/{owner_project_id}/tasks/{owner_task_id}/comments")

    assert response.status_code == 200
    assert len(response.json()) == 1


@pytest.mark.asyncio
async def test_get_comments_forbidden_for_non_member(test_client, owner_project_id, owner_task_id):
    await register_user(test_client, "Outsider", "outsider3@example.com")
    await login_user(test_client, "outsider3@example.com")

    response = await test_client.get(f"/projects/{owner_project_id}/tasks/{owner_task_id}/comments")

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_update_comment_happy_path(owner_client, owner_project_id, owner_task_id):
    created = await owner_client.post(
        f"/projects/{owner_project_id}/tasks/{owner_task_id}/comments",
        json={"text": "old"},
    )
    comment_id = created.json()["id"]

    response = await owner_client.patch(
        f"/projects/{owner_project_id}/tasks/{owner_task_id}/comments/{comment_id}",
        json={"text": "new"},
    )

    assert response.status_code == 200
    assert response.json() == {"success": True}


@pytest.mark.asyncio
async def test_update_comment_by_another_user_returns_403(test_client):
    await register_user(test_client, "Owner", "owner5@example.com")
    await login_user(test_client, "owner5@example.com")
    project_id = (await test_client.post("/projects", json={"name": "Comm"})).json()["id"]
    task_id = (
        await test_client.post(
            f"/projects/{project_id}/tasks",
            json={"title": "T", "description": "D", "assignee_email": "owner5@example.com"},
        )
    ).json()["id"]
    comment_id = (
        await test_client.post(
            f"/projects/{project_id}/tasks/{task_id}/comments",
            json={"text": "mine"},
        )
    ).json()["id"]

    await register_user(test_client, "Member", "member5@example.com")
    await test_client.post(f"/projects/{project_id}/members", json={"email": "member5@example.com"})
    await test_client.post("/users/auth/logout")
    await login_user(test_client, "member5@example.com")

    response = await test_client.patch(
        f"/projects/{project_id}/tasks/{task_id}/comments/{comment_id}",
        json={"text": "hacked"},
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_delete_comment_happy_path(owner_client, owner_project_id, owner_task_id):
    created = await owner_client.post(
        f"/projects/{owner_project_id}/tasks/{owner_task_id}/comments",
        json={"text": "to delete"},
    )
    comment_id = created.json()["id"]

    delete_response = await owner_client.delete(
        f"/projects/{owner_project_id}/tasks/{owner_task_id}/comments/{comment_id}"
    )
    list_response = await owner_client.get(f"/projects/{owner_project_id}/tasks/{owner_task_id}/comments")

    assert delete_response.status_code == 200
    assert list_response.status_code == 200
    assert list_response.json() == []


@pytest.mark.asyncio
async def test_delete_comment_not_found_returns_404(owner_client, owner_project_id, owner_task_id):
    response = await owner_client.delete(
        f"/projects/{owner_project_id}/tasks/{owner_task_id}/comments/9999"
    )

    assert response.status_code == 404
