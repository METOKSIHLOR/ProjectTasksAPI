from fastapi import FastAPI

from src.db.models import Base
from src.db.session import connect_db, close_db
from src.api.routers.users import router as users_router
from src.api.routers.tasks import router as tasks_router
from src.api.routers.projects import router as projects_router

async def lifespan(app: FastAPI):
    """жизненный цикл фастапи. При старте приложения открываем бд, при остановке закрываем"""
    await connect_db()

    yield

    await close_db()

app = FastAPI(lifespan=lifespan)

# добавляем роутеры
app.include_router(users_router)
app.include_router(projects_router)
app.include_router(tasks_router)