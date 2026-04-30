import asyncio
from fastapi import APIRouter, Cookie
from fastapi.websockets import WebSocket, WebSocketDisconnect

import src.db.session as sess
from src.api.websockets.utils import get_current_user, manager, session_watcher, UserAccessCache, \
    check_user_access, Limits
from src.core.exceptions.users_exceptions import UserNotAuthorizedException
from src.db.repositories.project_repo import ProjectRepository
from src.db.repositories.tasks_repo import TasksRepository

router = APIRouter()

@router.get("/ws", tags=["websockets"], summary="Информация о вебсокетах для документации")
async def websocket_docs_mock():
    """
    Фиктивный HTTP endpoint для документации real-time сценариев.

    Нужен чтобы в Swagger можно было явно увидеть контракт WebSocket: форматы
    подписки/отписки, ограничения и виды комнат.
    """
    return {
        "transport": "websocket",
        "endpoint": "/ws",
        "auth": "HttpOnly cookie `session_id`",
        "actions": ["subscribe", "unsubscribe"],
        "rooms": {
            "user:<uuid>": "личные события пользователя",
            "project:<uuid>": "события проекта для участников",
            "task:<uuid>": "события отдельной задачи",
        },
        "limits": {
            "max_rooms_per_user": Limits.MAX_ROOMS_PER_USER,
            "max_rooms_per_message": Limits.MAX_ROOMS_PER_MESSAGE,
            "write_queue_size": Limits.WRITE_QUEUE_SIZE,
            "send_timeout_seconds": Limits.SEND_TIMEOUT_SECONDS,
        },
        "notes": [
            "Подписка на user:<current_user_id> выполняется автоматически.",
            "Доступ к project/task комнатам валидируется по членству в проекте.",
            "При истечении сессии соединение закрывается с кодом 1008.",
        ],
    }

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, session_id: str = Cookie(None)):
    """
    Основной endpoint WebSocket.

    Поддерживает:
    - subscribe
    - unsubscribe
    """

    # первичная проверка сессии
    try:
        user_id = await get_current_user(session_id)
    except UserNotAuthorizedException:
        await websocket.close(code=1008)
        return

    await websocket.accept()
    await manager.register(websocket)

    # запускаем watcher сессии
    watcher_task = asyncio.create_task(
        session_watcher(websocket, session_id)
    )

    # автоматически подписываем на личную комнату
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
            if not isinstance(message_rooms, list) or len(message_rooms) > Limits.MAX_ROOMS_PER_MESSAGE:
                await manager.send_to_ws(
                    websocket,
                    {"success": False, "error": "Message too large."},
                )
                continue

            action = message.get("action")

            # фильтруем только валидные строки вида "type:id"
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
        # аккуратно останавливаем watcher
        watcher_task.cancel()
        try:
            await watcher_task
        except asyncio.CancelledError:
            pass

        # полностью чистим соединение
        await manager.disconnect_all(websocket)