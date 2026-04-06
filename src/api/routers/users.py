from fastapi import APIRouter, HTTPException
from fastapi import Response
from fastapi.params import Depends, Cookie
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.authorization.storage import storage
from src.api.dependencies import get_session, get_current_user
from src.api.schemas.user_schemas import (
    UserRegistrationSchema,
    UserResponseSchema,
    UserCredsSchema,
)
from src.services.user_services import UserServices

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "/registration",
    response_model=UserResponseSchema,
    summary="Зарегистрировать нового пользователя",
    responses={409: {"description": "Такая почта уже занята"}},
)
async def user_registration(
    user: UserRegistrationSchema, session: AsyncSession = Depends(get_session)
):
    """Добавление нового пользователя в бд"""
    service = UserServices(session)
    user = await service.register(user)  # добавляем пользователя
    return user


@router.post(
    "/auth/login",
    summary="Залогинить пользователя",
    responses={401: {"description": "Неверный логин или пароль"}},
)
async def user_login(
    user: UserCredsSchema,
    response: Response,
    session: AsyncSession = Depends(get_session),
):
    """Аутентификация пользователя через сессии и куки"""
    service = UserServices(session)
    """проверка входных данных пользователя и добавление айди сессии в редис в случае успеха"""
    session_id = await service.auth(user)

    response.set_cookie(
        key="session_id",  # добавление айди сессии в куки с временем жизни в 1 час
        value=session_id,
        max_age=3600,
        httponly=True,
        samesite="lax",
    )

    return {"success": True}


@router.post(
    "/auth/logout",
    summary="Разлогинить пользователя",
    responses={401: {"description": "Пользователь не авторизован"}},
)
async def user_logout(response: Response, session_id=Cookie(None)):
    """Разлогин пользователя и удаление его сессии из хранилища и куков"""

    if session_id is None:
        raise HTTPException(status_code=403, detail="Not authorized")

    response.delete_cookie(key="session_id")  # удаляем из куков сессию

    await storage.delete(session_id)  # удаляем из хранилища сессию

    return {"success": True}


@router.get(
    "/me",
    response_model=UserResponseSchema,
    summary="Получить профиль пользователя",
    responses={
        404: {"description": "Пользователь не найден"},
        401: {"description": "Пользователь не залогинен"},
    },
)
async def get_user_profile(
    user_id: int = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Пользователь получает данные о своем аккаунте, который определяется по номеру его сессии в куках"""
    service = UserServices(session)
    user = await service.get_user_by_id(user_id=user_id)  # получаем юзера
    return user
