import asyncio
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any
from uuid import UUID, uuid4

from fastapi.websockets import WebSocket

from src.core.exceptions.users_exceptions import UserNotAuthorizedException
from src.db.redis_storage import storage
from src.db.repositories.project_repo import ProjectRepository
from src.db.repositories.tasks_repo import TasksRepository

class Limits:
    # Ограничения для защиты от злоупотреблений
    MAX_ROOMS_PER_USER = 5          # сколько комнат может слушать один клиент
    MAX_ROOMS_PER_MESSAGE = 50      # сколько комнат можно передать в одном сообщении
    WRITE_QUEUE_SIZE = 200          # буфер исходящих сообщений на клиента
    SEND_TIMEOUT_SECONDS = 5        # таймаут отправки в websocket


async def get_current_user(session_id: str | None):
    """
    Проверяет сессию в Redis и возвращает user_id.
    Если сессии нет - считаем пользователя неавторизованным.
    """
    user_id = await storage.get(f"session_id:{session_id}")

    if user_id is None:
        raise UserNotAuthorizedException()

    return user_id


async def session_watcher(websocket: WebSocket, session_id: str):
    """
    Фоновая задача, которая периодически проверяет валидность сессии.

    Нужна потому, что WebSocket соединение живёт долго,
    а сессия может истечь или быть удалена (logout).
    """
    while True:
        await asyncio.sleep(30)

        try:
            await get_current_user(session_id)
        except UserNotAuthorizedException:
            # Если сессия больше невалидна - полностью отключаем клиента
            await manager.disconnect_all(websocket)
            await websocket.close(code=1008)
            break


@dataclass
class UserAccessCache:
    """
    Кэш прав доступа в рамках одного запроса subscribe.

    Позволяет не ходить в БД повторно для одних и тех же проектов/тасков.
    """
    projects: dict[UUID, bool] = field(default_factory=dict)
    tasks: dict[UUID, UUID | None] = field(default_factory=dict)


async def check_user_access(
    room: str,
    user_id: str,
    project_repo: ProjectRepository,
    task_repo: TasksRepository,
    cache: UserAccessCache,
):
    """
    Проверяет, имеет ли пользователь доступ к комнате.

    Формат комнаты:
    - user:<uuid>
    - project:<uuid>
    - task:<uuid>
    """
    try:
        resource_type, resource_id = room.split(":", 1)
        resource_uuid = UUID(resource_id)
        user_uuid = UUID(user_id)

        match resource_type:
            case "user":
                # пользователь может слушать только самого себя
                return resource_uuid == user_uuid

            case "project":
                # проверяем кэш
                if resource_uuid in cache.projects:
                    return cache.projects[resource_uuid]

                # проверяем членство в проекте
                member = await project_repo.get_project_member(
                    project_id=resource_uuid,
                    member_id=user_uuid,
                )
                has_access = member is not None
                cache.projects[resource_uuid] = has_access
                return has_access

            case "task":
                # сначала получаем project_id таски (с кэшем)
                if resource_uuid not in cache.tasks:
                    task = await task_repo.get_task_by_id(task_id=resource_uuid)
                    cache.tasks[resource_uuid] = task.project_id if task else None

                project_id = cache.tasks[resource_uuid]
                if project_id is None:
                    return False

                # проверяем доступ к проекту
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
        # если формат комнаты битый - просто запрещаем
        return False


@dataclass
class ClientConnection:
    """
    Состояние одного WebSocket клиента.
    """
    connection_id: str = field(default_factory=lambda: str(uuid4())) # уникальный айди клиента
    rooms: set[str] = field(default_factory=set)  # комнаты, на которые подписан клиент
    send_queue: asyncio.Queue[dict[str, Any]] = field(
        default_factory=lambda: asyncio.Queue(maxsize=Limits.WRITE_QUEUE_SIZE),
    )  # очередь сообщений на отправку
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)  # защита от гонок
    writer_task: asyncio.Task | None = None  # задача отправки сообщений


class ConnectionManager:
    """
    Управляет всеми WebSocket соединениями и подписками на комнаты.
    """

    def __init__(self):
        self.rooms: defaultdict[str, set[WebSocket]] = defaultdict(set)
        # room -> set(websockets)

        self.clients: dict[WebSocket, ClientConnection] = {}
        # websocket -> состояние клиента

    async def _writer(self, websocket: WebSocket):
        """
        Отдельная задача на клиента, которая отправляет сообщения из очереди.

        Нужна чтобы:
        - не блокировать основной loop
        - контролировать таймауты отправки
        """
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
                    timeout=Limits.SEND_TIMEOUT_SECONDS,
                )
        except Exception:
            # при любой ошибке - полностью отключаем клиента
            await self.disconnect_all(websocket)

    async def register(self, websocket: WebSocket):
        """
        Регистрирует новый WebSocket и запускает writer.
        """
        if websocket in self.clients:
            return

        client = ClientConnection()
        client.writer_task = asyncio.create_task(self._writer(websocket))
        self.clients[websocket] = client

        await manager.send_to_ws(websocket, {
            "type": "connection_established",
            "connection_id": client.connection_id,
        })

    async def connect(self, websocket: WebSocket, rooms: list[str]):
        """
        Подписывает клиента на комнаты.
        """
        client = self.clients.get(websocket)
        if client is None:
            return {"success": False, "error": "Connection is not registered."}

        async with client.lock:
            if not rooms:
                return {"success": False, "error": "Allowed rooms are empty"}

            current_rooms = client.rooms
            new_rooms = set(rooms) - current_rooms

            # проверка лимита
            if len(new_rooms) + len(current_rooms) > Limits.MAX_ROOMS_PER_USER:
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
        """
        Отписывает клиента от указанных комнат.
        """
        client = self.clients.get(websocket)
        if client is None:
            return

        async with client.lock:
            for room in rooms:
                if room.split(":", 1)[0] == 'user':
                   continue
                sockets = self.rooms.get(room)
                if not sockets:
                    continue

                sockets.discard(websocket)
                client.rooms.discard(room)

                if not sockets:
                    del self.rooms[room]

    async def disconnect_all(self, websocket: WebSocket):
        """
        Полностью удаляет клиента:
        - отписывает от всех комнат
        - останавливает writer
        """
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

        if client.writer_task:
            client.writer_task.cancel()

        self.clients.pop(websocket, None)

    async def send_to_ws(self, websocket: WebSocket, message: dict[str, Any], sender_ws: WebSocket | None = None):
        """
        Добавляет сообщение в очередь клиента.
        """
        client = self.clients.get(websocket)
        if client is None:
            return

        try:
            client.send_queue.put_nowait(message)
        except asyncio.QueueFull:
            # если клиент не успевает читать - отключаем
            await self.disconnect_all(websocket)

    async def send_to_room(
            self,
            room: str,
            message: dict[str, Any],
            sender_connection_id: str | None = None,
    ):
        """
        Рассылает сообщение всем клиентам в комнате.
        """
        for ws in list(self.rooms.get(room, [])):
            enriched_message = {
                **message,
                "origin_connection_id": sender_connection_id,
            }
            await self.send_to_ws(ws, enriched_message)

manager = ConnectionManager()