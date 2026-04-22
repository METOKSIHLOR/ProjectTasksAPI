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

router = APIRouter()

async def get_current_user(session_id):
    user_id = await storage.get(f"session_id:{session_id}")

    if user_id is None:
        raise UserNotAuthorizedException()

    return user_id

async def check_user_access(room: str, user_id: str, session: AsyncSession, extra_data: dict | None):
    try:
        resource_type, resource_id = room.split(":")

        match resource_type:
            case "user":
                return UUID(resource_id) == UUID(user_id)
            case "project":
                repo = ProjectRepository(session)
                member = await repo.get_project_member(project_id=UUID(resource_id), member_id=UUID(user_id))
                return member is not None

            case "task":
                if not extra_data or extra_data.get("project_id", None) is None:
                    return False
                project = extra_data["project_id"]
                task_repo = TasksRepository(session)
                project_repo = ProjectRepository(session)
                if await project_repo.get_project_member(project_id=UUID(project), member_id=UUID(user_id)):
                    if await task_repo.get_task_by_project(task_id=UUID(resource_id), project_id=UUID(project)):
                        return True
                return False

            case _:
                return False
    except (TypeError, ValueError):
        return False

class ConnectionManager:
    def __init__(self):
        self.rooms = defaultdict(list)

    async def connect(self, websocket: WebSocket, rooms: List[str]):
        """Подключить websocket к одной или нескольким комнатам."""
        for room in rooms:
            if websocket not in self.rooms[room]:
                self.rooms[room].append(websocket)

    def disconnect(self, websocket: WebSocket, rooms: List[str]):
        """Отключить websocket от указанных комнат."""
        for room in rooms:
            self.rooms[room].remove(websocket)

    def disconnect_all(self, websocket: WebSocket):
        """Отключить websocket от всех комнат."""
        for room in self.rooms.values():
            if websocket in room:
                room.remove(websocket)

    async def send_to_room(self, room: str, message: dict):
        """Отправить сообщение всем участникам комнаты."""
        for ws in self.rooms[room]:
            try:
                await ws.send_json(message)
            except Exception as e:
                print(e)
                # Если не удалось отправить сообщение (например, websocket отключен),
                # отключаем его от всех комнат.
                self.disconnect_all(ws)


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
            message = await websocket.receive_json()
            action = message.get("action")
            rooms = message.get("rooms", [])
            extra_data = message.get("extra_data", None)

            # Обработка различных действий с помощью match
            match action:
                case "subscribe":
                    allowed_rooms = []
                    async with sess.SessionFactory() as session:
                        for room in rooms:
                            if await check_user_access(room=room, user_id=user_id, session=session, extra_data=extra_data):
                                allowed_rooms.append(room)
                    answer = {"success": True} if len(allowed_rooms) > 0 else {"success": False}
                    await manager.connect(websocket, allowed_rooms)
                    await websocket.send_json(answer)

                case "unsubscribe":
                    if rooms:
                        manager.disconnect(websocket, rooms)

                case _:
                    # Если действие не распознано
                    await websocket.send_json({"error": "Invalid action"})
    except WebSocketDisconnect:
        # Отключение от всех комнат при разрыве соединения
        manager.disconnect_all(websocket)
        await websocket.close()
    except Exception as e:
        await websocket.send_json({"error": str(e)})
        manager.disconnect_all(websocket)
