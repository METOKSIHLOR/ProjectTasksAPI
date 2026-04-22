from typing import List
from uuid import UUID

from fastapi import APIRouter, Cookie
from fastapi.websockets import WebSocket, WebSocketDisconnect

from collections import defaultdict

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions.users_exceptions import UserNotAuthorizedException
from src.db.redis_storage import storage
import src.db.session as sess
from src.db.repositories.project_repo import ProjectRepository
from src.db.repositories.tasks_repo import TasksRepository

import asyncio
router = APIRouter()

MAX_ROOMS_PER_USER = 5

async def get_current_user(session_id):
    user_id = await storage.get(f"session_id:{session_id}")

    if user_id is None:
        raise UserNotAuthorizedException()

    return user_id

async def check_user_access(room: str, user_id: str, session: AsyncSession, repos: dict):
    try:
        resource_type, resource_id = room.split(":", 1)

        match resource_type:
            case "user":
                return UUID(resource_id) == UUID(user_id)
            case "project":
                repo = repos['project_repo']
                member = await repo.get_project_member(project_id=UUID(resource_id), member_id=UUID(user_id))
                return member is not None

            case "task":
                task_repo = repos['task_repo']
                project_repo = repos['project_repo']
                task = await task_repo.get_task_by_id(task_id=UUID(resource_id))
                if not task:
                    return False
                return await project_repo.get_project_member(project_id=task.project_id, member_id=UUID(user_id))
            case _:
                return False
    except (TypeError, ValueError):
        return False

class ConnectionManager:
    def __init__(self):
        self.rooms = defaultdict(set)
        self.ws_rooms = defaultdict(set)
        self.locks: dict[WebSocket, asyncio.Lock] = {}

    async def connect(self, websocket: WebSocket, rooms: List[str]):
        """Подключить websocket к одной или нескольким комнатам."""
        lock = self.locks.setdefault(websocket, asyncio.Lock())
        async with lock:
            current_rooms = self.ws_rooms[websocket]
            if len(rooms) == 0:
                return {"success": False,
                        "error": "Allowed rooms are empty"}

            new_rooms = set(rooms) - current_rooms
            if len(new_rooms) + len(current_rooms) > MAX_ROOMS_PER_USER:
                return {"success": False,
                        "error": "The rooms limit has been reached."}

            for room in new_rooms:
                self.rooms[room].add(websocket)
                self.ws_rooms[websocket].add(room)
            return {"success": True,
                    "rooms": list(new_rooms),}

    async def disconnect(self, websocket: WebSocket, rooms: List[str]):
        """Отключить websocket от указанных комнат."""
        lock = self.locks.setdefault(websocket, asyncio.Lock())
        async with lock:
            for room in rooms:
                sockets = self.rooms.get(room)
                if not sockets:
                    continue

                sockets.discard(websocket)

                self.ws_rooms[websocket].discard(room)

                if not sockets:
                    del self.rooms[room]

    async def disconnect_all(self, websocket: WebSocket):
        lock = self.locks.setdefault(websocket, asyncio.Lock())
        async with lock:
            for room in list(self.ws_rooms.get(websocket, set())):
                sockets = self.rooms.get(room)
                if sockets:
                    sockets.discard(websocket)
                    if not sockets:
                        del self.rooms[room]

            self.ws_rooms.pop(websocket, None)
        self.locks.pop(websocket, None)

    async def send_to_room(self, room: str, message: dict):
        """Отправить сообщение всем участникам комнаты."""
        to_disconnect = []

        for ws in list(self.rooms.get(room, [])):
            try:
                await ws.send_json(message)
            except Exception:
                to_disconnect.append(ws)

        for ws in to_disconnect:
            await self.disconnect_all(ws)

manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, session_id: str = Cookie(None)):
    try:
        user_id = await get_current_user(session_id)
    except UserNotAuthorizedException as e:
        await websocket.close()
        return e

    await websocket.accept()

    rooms = [f"user:{user_id}"]
    await manager.connect(websocket, rooms)

    try:
        while True:
            try:
                message = await websocket.receive_json()
            except Exception:
                continue

            if len(message.get("rooms", [])) > 50:
                await websocket.send_json({"success": False,
                                           "error": "Message too large."})
                continue

            action = message.get("action")
            rooms = [
                r for r in set(message.get("rooms", []))
                if isinstance(r, str) and ":" in r
            ]
            # Обработка различных действий с помощью match
            match action:
                case "subscribe":
                    allowed_rooms = []
                    async with sess.SessionFactory() as session:
                        repos = {
                            "project_repo": ProjectRepository(session),
                            "task_repo": TasksRepository(session),
                        }
                        for room in rooms:
                            if await check_user_access(room=room, user_id=user_id, session=session, repos=repos):
                                allowed_rooms.append(room)

                    result = await manager.connect(websocket, allowed_rooms)

                    await websocket.send_json(result)

                case "unsubscribe":
                    if rooms:
                        await manager.disconnect(websocket, rooms)

                case _:
                    # Если действие не распознано
                    await websocket.send_json({"success": False,
                                               "error": "Invalid action"})
    except Exception as e:
        await websocket.send_json({"success": False,
                                   "error": str(e)})
    finally:
        await manager.disconnect_all(websocket)
