from typing import List

from fastapi import APIRouter, Cookie
from fastapi.websockets import WebSocket, WebSocketDisconnect

from collections import defaultdict

from src.core.exceptions.users_exceptions import UserNotAuthorizedException
from src.db.redis_storage import storage

router = APIRouter()

async def get_current_user(session_id):
    user_id = await storage.get(f"session_id:{session_id}")

    if user_id is None:
        raise UserNotAuthorizedException()

    return user_id

class ConnectionManager:
    def __init__(self):
        self.rooms = defaultdict(list)

    async def connect(self, websocket: WebSocket, rooms: List[str]):
        """Подключить websocket к одной или нескольким комнатам."""
        for room in rooms:
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
            except Exception:
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
        raise e

    await websocket.accept()

    rooms = [f"user:{user_id}"]
    await manager.connect(websocket, rooms)

    try:
        while True:
            message = await websocket.receive_json()
            action = message.get("action")
            rooms = message.get("rooms", [])

            # Обработка различных действий с помощью match
            match action:
                case "subscribe":
                    if rooms:
                        await manager.connect(websocket, rooms)
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
        # В случае непредвиденной ошибки можно обработать и закрыть соединение
        await websocket.send_json({"error": str(e)})
        manager.disconnect_all(websocket)
