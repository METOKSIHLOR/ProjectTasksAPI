from typing import List
from uuid import UUID

from fastapi import APIRouter, Header
from fastapi import Response
from fastapi.params import Depends, Cookie
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions.users_exceptions import UserNotAuthorizedException
from src.db.redis_storage import storage
from src.api.dependencies import get_session, get_current_user
from src.api.schemas.user_schemas import (
    UserRegistrationSchema,
    UserResponseSchema,
    UserCredsSchema, UpdateUserSchema, UserSettingsResponseSchema, UpdateUserSettingsSchema, UserInvitesInfoSchema,
    UserInvitesUpdateSchema, UserResponseWithRelationsSchema,
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
        raise UserNotAuthorizedException()

    response.delete_cookie(key="session_id")  # удаляем из куков сессию

    await storage.delete(f"session_id:{session_id}")  # удаляем из хранилища сессию

    return {"success": True}


@router.get(
    "/me",
    summary="Получить профиль пользователя",
    responses={
        401: {"description": "Пользователь не авторизован"},
    },
)
async def get_user_profile(
    user_id: UUID = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> UserResponseWithRelationsSchema:
    """Пользователь получает данные о своем аккаунте, который определяется по номеру его сессии в куках"""
    service = UserServices(session)
    user = await service.get_user_by_id_with_rels(user_id=user_id)  # получаем юзера с его настройками и инвайтами
    return user

@router.get("/invites",
            summary="Получение приглашений пользователя",
            responses={
                401: {"description": "Пользователь не авторизован"},
            })
async def get_user_invites(session: AsyncSession = Depends(get_session),
                           user_id: UUID = Depends(get_current_user)) -> List[UserInvitesInfoSchema]:
    """Ручка возвращает все приглашения пользователя, которые в данный момент ожидают рассмотрения"""
    service = UserServices(session)
    invites = await service.get_user_invites(user_id=user_id)
    return invites

@router.delete("/invites/{invite_id}",
              summary="Изменить статус приглашения",
              responses={
                  401: {"description": "Пользователь не авторизован"},
                  404: {"description": "Приглашение не найдено"}
              })
async def invite_solution(invite_id: UUID,
                               solution: UserInvitesUpdateSchema,
                               user_id: UUID = Depends(get_current_user),
                               x_connection_id: str | None = Header(None),
                               session: AsyncSession = Depends(get_session)):
    """Ручка позволяет принять/отклонить приглашение в группу.
     Если пользователь его принимает - он добавляется в указанный проект"""
    service = UserServices(session)
    await service.accept_or_deny_invite(user_id=user_id, invite_id=invite_id, solution=solution, connection_id=x_connection_id)
    return {"success": True}


@router.patch("/me", summary="Обновить данные пользователя",
              responses={
                  401: {"description": "Пользователь не авторизован"},
                  409: {"description": "Такая почта уже занята"}
              })
async def update_user_profile(
    update: UpdateUserSchema,
    user_id: UUID = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Обновляет пока что только никнейм и почту"""
    service = UserServices(session)
    await service.update_user_profile(user_id=user_id, new_details=update)
    return {"success": True}

@router.put("/settings", summary="Обновить настройки пользователя",)
async def update_user_settings(new_settings: UpdateUserSettingsSchema,
                               user_id: UUID = Depends(get_current_user),
                               session: AsyncSession = Depends(get_session),
                               ) -> UserSettingsResponseSchema:
    service = UserServices(session)
    settings = await service.update_user_settings(user_id=user_id, new_settings=new_settings)
    return settings