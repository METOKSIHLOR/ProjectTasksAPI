from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config.config import config
from src.core.exceptions.base_exception import BaseAPIException
from src.core.handlers import exception_handler
from src.core.middleware import LoggingMiddleware
from src.db.session import connect_db, close_db
from src.api.routers.users import router as users_router
from src.api.routers.tasks import router as tasks_router
from src.api.routers.projects import router as projects_router
from src.api.routers.comments import router as comments_router
from src.api.routers.websockets import router as websockets_router

async def lifespan(app: FastAPI):
    """жизненный цикл фастапи. При старте приложения открываем бд, при остановке закрываем"""
    await connect_db()

    yield

    await close_db()

app = FastAPI(lifespan=lifespan,
              title="Tasks Management API",
              description=
              """
API для управления проектами, задачами и комментариями с cookie-based авторизацией.

## Основные сущности
- Пользователи
- Проекты
- Задачи
- Комментарии

## Что умеет API
- Регистрация/аутентификация/обновление данных пользователя
- Создание/обновление/удаление проектов
- Управление участниками проекта (owner/member)
- Создание и ведение задач внутри проекта
- Комментирование задач

## Авторизация
- Логин создает HttpOnly cookie `session_id`
- Защищенные ручки требуют валидную сессию
- Логаут удаляет сессию и cookie

## Типовые коды ответов
- `200` — успешная операция
- `401` — пользователь не авторизован
- `403` — недостаточно прав
- `404` — сущность не найдена
- `409` — конфликт данных
              """,
              version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.cors.origins,
    allow_credentials=True,
    allow_methods=config.cors.methods,
    allow_headers=config.cors.headers,
)

# добавляем миддлвари
app.add_middleware(LoggingMiddleware)

# добавляем обработчики ошибок
app.add_exception_handler(BaseAPIException, exception_handler)

# добавляем роутеры
app.include_router(users_router)
app.include_router(projects_router)
app.include_router(tasks_router)
app.include_router(comments_router)
app.include_router(websockets_router)