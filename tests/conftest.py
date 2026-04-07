import os
from collections.abc import AsyncGenerator

import httpx
import pytest_asyncio
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from tests.helpers import login_user, register_user

# Минимальный набор env-переменных, чтобы импортировать config/app в тестах.
os.environ.setdefault("POSTGRES_USER", "test")
os.environ.setdefault("POSTGRES_PASSWORD", "test")
os.environ.setdefault("POSTGRES_DB", "test")
os.environ.setdefault("POSTGRES_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("REDIS_HOST", "localhost")
os.environ.setdefault("REDIS_PORT", "6379")
os.environ.setdefault("REDIS_DB", "0")
os.environ.setdefault("ALLOW_ORIGINS", "http://localhost")
os.environ.setdefault("ALLOW_METHODS", "*")
os.environ.setdefault("ALLOW_HEADERS", "*")


from src.api.dependencies import get_session
from src.api.main import app
from src.db.models import Base


class InMemoryStorage:
    def __init__(self):
        self._data: dict[str, str] = {}

    async def set(self, key: str, value: int, ex: int | None = None):
        self._data[key] = str(value)

    async def get(self, key: str):
        return self._data.get(key)

    async def delete(self, key: str):
        self._data.pop(key, None)


@pytest_asyncio.fixture
async def db_sessionmaker() -> AsyncGenerator[async_sessionmaker, None]:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_maker = async_sessionmaker(engine, expire_on_commit=False)
    try:
        yield session_maker
    finally:
        await engine.dispose()


@pytest_asyncio.fixture
async def test_client(db_sessionmaker, monkeypatch) -> AsyncGenerator[httpx.AsyncClient, None]:
    fake_storage = InMemoryStorage()
    monkeypatch.setattr(storage, "set", fake_storage.set)
    monkeypatch.setattr(storage, "get", fake_storage.get)
    monkeypatch.setattr(storage, "delete", fake_storage.delete)

    async def override_get_session():
        async with db_sessionmaker() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def owner_client(test_client: httpx.AsyncClient) -> httpx.AsyncClient:
    await register_user(test_client, "Owner User", "owner@example.com")
    login_response = await login_user(test_client, "owner@example.com")
    assert login_response.status_code == 200
    return test_client


@pytest_asyncio.fixture
async def member_client(test_client: httpx.AsyncClient) -> httpx.AsyncClient:
    await register_user(test_client, "Member User", "member@example.com")
    return test_client


@pytest_asyncio.fixture
async def owner_project_id(owner_client: httpx.AsyncClient) -> int:
    response = await owner_client.post("/projects", json={"name": "Alpha project"})
    assert response.status_code == 200
    return response.json()["id"]


@pytest_asyncio.fixture
async def owner_task_id(owner_client: httpx.AsyncClient, owner_project_id: int) -> int:
    response = await owner_client.post(
        f"/projects/{owner_project_id}/tasks",
        json={
            "title": "Initial task",
            "description": "Seed task",
            "assignee_email": "owner@example.com",
        },
    )
    assert response.status_code == 200
    return response.json()["id"]
