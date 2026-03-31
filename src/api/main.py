from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from src.config.config import config
from src.db.session import connect_db, close_db
from src.api.routers.users import router as users_router
from src.api.routers.tasks import router as tasks_router
from src.api.routers.projects import router as projects_router
from src.api.routers.comments import router as comments_router

async def lifespan(app: FastAPI):
    """жизненный цикл фастапи. При старте приложения открываем бд, при остановке закрываем"""
    await connect_db()

    yield

    await close_db()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.cors.origins,
    allow_credentials=True,
    allow_methods=config.cors.methods,
    allow_headers=config.cors.headers,
)

# добавляем роутеры
app.include_router(users_router)
app.include_router(projects_router)
app.include_router(tasks_router)
app.include_router(comments_router)