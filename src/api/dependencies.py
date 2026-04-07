import uuid
from uuid import UUID

from fastapi import Cookie, Depends, HTTPException, Path
from src.db.repositories.user_repo import UserRepository
import src.db.session as sess
from src.db.redis_storage import storage


async def get_session():
    """Получаем сессию для ручек через фабрику сессий"""
    async with sess.SessionFactory() as session:
        yield session

async def get_current_user(session_id = Cookie(None)):
    """обращаемся в куки пользователя и достаем оттуда айди его сессии, из которого достаем в хранилище его айди"""
    if session_id is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user_id = await storage.get(f"session_id:{session_id}") # достаем айди из редиса

    if user_id is None: # если сессия в куках не совпадает с сессиями в хранилище
        raise HTTPException(status_code=401, detail="Invalid session")

    return uuid.UUID(user_id)

class CheckUserPerms:
    def __init__(self, roles: list):
        self.roles = roles

    async def __call__(self,
                       user_id = Depends(get_current_user),
                       project_id: UUID = Path(...),
                       session = Depends(get_session)):
        repo = UserRepository(session=session)
        access = await repo.check_user_role(user_id=user_id, project_id=project_id, roles=self.roles)
        
        if not access:
            raise HTTPException(status_code=403, detail="Not authorized")

