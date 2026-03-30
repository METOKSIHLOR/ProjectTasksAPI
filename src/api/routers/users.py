from fastapi import APIRouter, HTTPException
from fastapi import Response
from fastapi.params import Depends, Query, Cookie
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.authorization.storage import storage
from src.api.dependencies import get_session, get_current_user
from src.api.schemas.user_schemas import UserRegistrationSchema, UserResponseSchema, UserLoginSchema
from src.db.repositories.user_repo import UserRepository
from src.services.user_services import UserServices

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/registration", response_model=UserResponseSchema)
async def register_user(user: UserRegistrationSchema, session: AsyncSession = Depends(get_session)):
    """Добавление нового пользователя в бд"""
    service = UserServices(session)
    try:
        user = await service.register(user) # добавляем пользователя
    except IntegrityError: # если имя или почта уже заняты
        await session.rollback()
        raise HTTPException(status_code=400, detail="This email already exists")
    return user

@router.post("/auth/login")
async def login(user: UserLoginSchema, response: Response, session: AsyncSession = Depends(get_session)):
    """Ручка реализует аутентификацию пользователя через сесси и куки"""
    service = UserServices(session)
    """проверка входных данных пользователя и добавление айди сессии в редис в случае успеха"""
    session_id = await service.auth(user)
    response.set_cookie(key="session_id", #добавление айди сессии в куки с временем жизни в 1 час
                        value=session_id,
                        max_age=3600,
                        httponly=True,
                        samesite="lax")

    return {"success": True}

@router.post("/auth/logout")
async def logout(response: Response, session_id = Cookie(None)):
    """Разлогин пользователя. Тут все просто"""

    if not session_id:
        raise HTTPException(status_code=401, detail="Not authorized")

    response.delete_cookie(key="session_id") # удаляем из куков сессию

    storage.delete(session_id) # удаляем из хранилища сессию

    return {"success": True}

@router.get("/me", response_model=UserResponseSchema)
async def get_user(user_id: int = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    """Пользователь получает данные о своем аккаунте, айди узнается по номеру его сессии в куках"""
    service = UserServices(session)
    user = await service.get_user_by_id(user_id) # получаем юзера
    return user
