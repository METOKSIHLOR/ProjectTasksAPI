import uuid
from uuid import UUID

from fastapi import Request, Depends, Path

from src.core.exceptions.users_exceptions import UserNotAuthorizedException, UserNotAuthenticatedException
from src.db.repositories.user_repo import UserRepository
import src.db.session as sess


async def get_session():
    """Получаем сессию для ручек через фабрику сессий"""
    async with sess.SessionFactory() as session:
        yield session

async def get_current_user(request: Request):
    """Достаем из миддлвари айди пользователя, если он авторизирован"""
    user_id = getattr(request.state, "user_id", None)

    if user_id is None: # если пользователь не авторизирован
        raise UserNotAuthorizedException()

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
            raise UserNotAuthenticatedException()

