from fastapi import Cookie, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import src.db.session as sess
from src.api.authorization.storage import storage


async def get_session():
    """Получаем сессию для ручек через фабрику сессий"""
    async with sess.SessionFactory() as session:
        yield session

async def get_current_user(session_id = Cookie(None)):
    """обращаемся в куки пользователя и достаем оттуда айди его сессии, из которого достаем в хранилище его айди"""
    if session_id is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user_id = storage.get(session_id) # достаем айди из редиса

    if user_id is None: # если сессия в куках не совпадает с сессиями в хранилище
        raise HTTPException(status_code=401, detail="Invalid session")

    return int(user_id)

