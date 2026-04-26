import asyncio
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Cookie
from fastapi.websockets import WebSocket, WebSocketDisconnect

import src.db.session as sess
from src.core.exceptions.users_exceptions import UserNotAuthorizedException
from src.db.redis_storage import storage
from src.db.repositories.project_repo import ProjectRepository
from src.db.repositories.tasks_repo import TasksRepository

router = APIRouter()

MAX_ROOMS_PER_USER = 5
MAX_ROOMS_PER_MESSAGE = 50
WRITE_QUEUE_SIZE = 200
SEND_TIMEOUT_SECONDS = 5


async def get_current_user(session_id: str | None):
    user_id = await storage.get(f"session_id:{session_id}")

    if user_id is None:
        raise UserNotAuthorizedException()

    return user_id

async def session_watcher(websocket: WebSocket, session_id: str):
    while True:
        await asyncio.sleep(30)

        try:
            await get_current_user(session_id)
        except UserNotAuthorizedException:
            await manager.disconnect_all(websocket)
            break


@dataclass
class UserAccessCache:
    projects: dict[UUID, bool] = field(default_factory=dict)
    tasks: dict[UUID, UUID | None] = field(default_factory=dict)


async def check_user_access(
    room: str,
    user_id: str,
    project_repo: ProjectRepository,
    task_repo: TasksRepository,
    cache: UserAccessCache,
):
    try:
        resource_type, resource_id = room.split(":", 1)
        resource_uuid = UUID(resource_id)
        user_uuid = UUID(user_id)

        match resource_type:
            case "user":
                return resource_uuid == user_uuid

            case "project":
                if resource_uuid in cache.projects:
                    return cache.projects[resource_uuid]

                member = await project_repo.get_project_member(
                    project_id=resource_uuid,
                    member_id=user_uuid,
                )
                has_access = member is not None
                cache.projects[resource_uuid] = has_access
                return has_access

            case "task":
                if resource_uuid not in cache.tasks:
                    task = await task_repo.get_task_by_id(task_id=resource_uuid)
                    cache.tasks[resource_uuid] = task.project_id if task else None

                project_id = cache.tasks[resource_uuid]
                if project_id is None:
                    return False

                if project_id in cache.projects:
                    return cache.projects[project_id]

                member = await project_repo.get_project_member(
                    project_id=project_id,
                    member_id=user_uuid,
                )
                has_access = member is not None
                cache.projects[project_id] = has_access
                return has_access

            case _:
                return False

    except (TypeError, ValueError):
        return False


@dataclass
class ClientConnection:
    rooms: set[str] = field(default_factory=set)
    send_queue: asyncio.Queue[dict[str, Any]] = field(
        default_factory=lambda: asyncio.Queue(maxsize=WRITE_QUEUE_SIZE),
    )
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)
    writer_task: asyncio.Task | None = None


class ConnectionManager:
    def __init__(self):
        self.rooms: defaultdict[str, set[WebSocket]] = defaultdict(set)
        self.clients: dict[WebSocket, ClientConnection] = {}

    async def _writer(self, websocket: WebSocket):
        client = self.clients.get(websocket)
        if client is None:
            return

        try:
            while True:
                payload = await client.send_queue.get()
                if payload is None:
                    return

                await asyncio.wait_for(
                    websocket.send_json(payload),
                    timeout=SEND_TIMEOUT_SECONDS,
                )
        except Exception:
            await self.disconnect_all(websocket)

    async def register(self, websocket: WebSocket):
        if websocket in self.clients:
            return

        client = ClientConnection()
        client.writer_task = asyncio.create_task(self._writer(websocket))
        self.clients[websocket] = client

    async def connect(self, websocket: WebSocket, rooms: list[str]):
        client = self.clients.get(websocket)
        if client is None:
            return {"success": False, "error": "Connection is not registered."}

        async with client.lock:
            if not rooms:
                return {"success": False, "error": "Allowed rooms are empty"}

            current_rooms = client.rooms
            new_rooms = set(rooms) - current_rooms

            if len(new_rooms) + len(current_rooms) > MAX_ROOMS_PER_USER:
                return {
                    "success": False,
                    "error": "The rooms limit has been reached.",
                }

            for room in new_rooms:
                self.rooms[room].add(websocket)
                current_rooms.add(room)

            return {
                "success": True,
                "rooms": list(new_rooms),
            }

    async def disconnect(self, websocket: WebSocket, rooms: list[str]):
        client = self.clients.get(websocket)
        if client is None:
            return

        async with client.lock:
            for room in rooms:
                sockets = self.rooms.get(room)
                if not sockets:
                    continue

                sockets.discard(websocket)
                client.rooms.discard(room)

                if not sockets:
                    del self.rooms[room]

    async def disconnect_all(self, websocket: WebSocket):
        client = self.clients.get(websocket)
        if client is None:
            return

        async with client.lock:
            for room in list(client.rooms):
                sockets = self.rooms.get(room)
                if sockets:
                    sockets.discard(websocket)
                    if not sockets:
                        del self.rooms[room]
                client.rooms.discard(room)

        client.writer_task.cancel()
        self.clients.pop(websocket, None)

    async def send_to_ws(self, websocket: WebSocket, message: dict[str, Any]):
        client = self.clients.get(websocket)
        if client is None:
            return

        try:
            client.send_queue.put_nowait(message)
        except asyncio.QueueFull:
            await self.disconnect_all(websocket)

    async def send_to_room(self, room: str, message: dict[str, Any]):
        print("sending to room", room, message)
        for ws in list(self.rooms.get(room, [])):
            await self.send_to_ws(ws, message)


manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, session_id: str = Cookie(None)):
    try:
        user_id = await get_current_user(session_id)
    except UserNotAuthorizedException:
        await websocket.close(code=1008)
        return

    await websocket.accept()
    await manager.register(websocket)

    watcher_task = asyncio.create_task(
        session_watcher(websocket, session_id)
    )

    await manager.connect(websocket, [f"user:{user_id}"])

    try:
        while True:
            try:
                message = await websocket.receive_json()
            except WebSocketDisconnect:
                break
            except Exception:
                await manager.send_to_ws(
                    websocket,
                    {"success": False, "error": "Invalid message format"},
                )
                continue

            if not isinstance(message, dict):
                await manager.send_to_ws(
                    websocket,
                    {"success": False, "error": "Invalid message format"},
                )
                continue

            message_rooms = message.get("rooms", [])
            if not isinstance(message_rooms, list) or len(message_rooms) > MAX_ROOMS_PER_MESSAGE:
                await manager.send_to_ws(
                    websocket,
                    {"success": False, "error": "Message too large."},
                )
                continue

            action = message.get("action")
            rooms = [
                room
                for room in set(message_rooms)
                if isinstance(room, str) and ":" in room
            ]

            match action:
                case "subscribe":
                    allowed_rooms: list[str] = []
                    if rooms:
                        async with sess.SessionFactory() as session:
                            project_repo = ProjectRepository(session)
                            task_repo = TasksRepository(session)
                            cache = UserAccessCache()

                            for room in rooms:
                                has_access = await check_user_access(
                                    room=room,
                                    user_id=user_id,
                                    project_repo=project_repo,
                                    task_repo=task_repo,
                                    cache=cache,
                                )
                                if has_access:
                                    allowed_rooms.append(room)

                    result = await manager.connect(websocket, allowed_rooms)
                    await manager.send_to_ws(websocket, result)

                case "unsubscribe":
                    if rooms:
                        await manager.disconnect(websocket, rooms)

                case _:
                    await manager.send_to_ws(
                        websocket,
                        {"success": False, "error": "Invalid action"},
                    )
    finally:
        watcher_task.cancel()
        try:
            await watcher_task
        except asyncio.CancelledError:
            pass

        await manager.disconnect_all(websocket)