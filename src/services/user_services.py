from typing import List
from fastapi.params import Cookie

from src.api.authorization.hash import hash_password, verify_password
from src.api.routers.websockets import manager
from src.core.exceptions.users_exceptions import ConflictEmailException, InvalidUserCredentialsException, \
    UserNotFoundException, UserNotAuthorizedException, UserInviteNotFoundException, ConflictInviteException

from src.api.schemas.user_schemas import UserRegistrationSchema, UserCredsSchema, UpdateUserSettingsSchema, \
    UserSettingsResponseSchema, UpdateUserSchema, UserInvitesInfoSchema, UserInvitesUpdateSchema
from src.db.models import User, UserSettings, UserInvite, ProjectMember
from src.db.redis_storage import storage
from src.db.repositories.project_repo import ProjectRepository
from src.db.repositories.user_repo import UserRepository
import uuid
from uuid import UUID



class UserServices:
    def __init__(self, session):
        self.repo = UserRepository(session)

    async def register(self, schema: UserRegistrationSchema):
        hash_pw = hash_password(schema.password) # хешируем пароль юзера
        model = User(name=schema.name, email=schema.email, hash_password=hash_pw, settings=UserSettings(settings={}))

        email_exist = await self.repo.get_user_by_email(email=schema.email) # проверяем существует ли уже такая почта в бд

        if email_exist is not None:
             raise ConflictEmailException(email=schema.email) # если существует - кидаем 409 ошибку
        
        user = await self.repo.create_user(model)

        await self.repo.commit()

        return user

    async def auth(self, schema: UserCredsSchema, session_id: str | None = Cookie(None)):
        if session_id is not None: # проверяем залогинен ли пользователь в данный момент
            await storage.delete(f"session_id:{session_id}") # если да - удаляем его текущую сессию, чтоб не копились

        user = await self.repo.get_user_by_email(schema.email)

        # если почта не найдена в бд или неверный пароль
        if user is None or not verify_password(schema.password, user.hash_password):
            raise InvalidUserCredentialsException()

        session_id = str(uuid.uuid4()) # назначаем новую сессию

        await storage.set("session_id:" + session_id, str(user.id), ex=3600) # добавляем сессию в хранилище

        return session_id


    async def get_user_by_email(self, email):
        user = await self.repo.get_user_by_email(email=email)

        if user is None:
            raise UserNotFoundException(user_cred=email)
        
        return user

    async def get_user_by_id(self, user_id: UUID):
        user = await self.repo.get_user_by_id(user_id=user_id)

        if user is None:
            raise UserNotFoundException(user_cred=user_id)
        
        return user

    async def add_user_invite(self, project_id: UUID, member_id: UUID, connection_id):
        exists = await self.repo.get_user_invite_by_project_id(user_id=member_id, project_id=project_id)

        if exists is not None:
            raise ConflictInviteException(member_id=member_id)

        invite = await self.repo.add_user_invite(invite=UserInvite(project_id=project_id, user_id=member_id))

        await self.repo.commit()

        await manager.send_to_room(f"user:{member_id}",
                                   {"type": "invite_create",
                                    "project_id": str(project_id)},
                                   sender_connection_id=connection_id)

        return invite

    async def get_user_invites(self, user_id: UUID):
        invites = await self.repo.get_user_invites(user_id=user_id)

        # маппим модели для получения дополнительных полей
        return [UserInvitesInfoSchema(id=invite.id,
                                      user_id=invite.user_id,
                                      project_id=invite.project_id,
                                      project_name=invite.project.name,
                                      project_author_email=invite.project.owner.email) for invite in invites]

    async def accept_or_deny_invite(self, user_id: UUID, invite_id: UUID, solution: UserInvitesUpdateSchema, connection_id):
        invite = await self.repo.get_user_invite_by_id(user_id=user_id, invite_id=invite_id)

        if invite is None:
            raise UserInviteNotFoundException(user_cred=user_id, invite_id=invite_id)

        # если пользователь принимает приглашение добавляем его
        if solution.status == "accepted":
            project_repo = ProjectRepository(session=self.repo.session)
            member = await project_repo.add_member(ProjectMember(user_id=invite.user_id, project_id=invite.project_id,))

            await manager.send_to_room(f"project:{invite.project_id}",
                                       {"type": "invite_accept",
                                        "user_email": invite.user.email,
                                        "user_name": invite.user.name,
                                        "user_role": member.role},
                                       sender_connection_id=connection_id)

        await self.repo.delete_user_invite(invite=invite)
        await self.repo.commit()
        return invite

    async def update_user_profile(self, user_id: UUID, new_details: UpdateUserSchema):
        if new_details.email is not None:
            existing_user = await self.repo.get_user_by_email(email=new_details.email)
            if existing_user:
                raise ConflictEmailException(email=new_details.email)

        user = await self.repo.get_user_by_id(user_id=user_id)

        await self.repo.update_user_profile(user=user, new_details=new_details.model_dump())

        await self.repo.commit()

        return user
    async def get_user_projects(self, user_id: UUID):
        projects = await self.repo.get_user_projects(user_id)
        return projects

    async def get_user_settings(self, user_id: UUID):
        user = await self.get_user_by_id(user_id=user_id)
        settings = user.settings.settings
        return UserSettingsResponseSchema(settings=settings)

    async def update_user_settings(self, user_id: UUID, new_settings: UpdateUserSettingsSchema):
        user = await self.get_user_by_id(user_id=user_id)
        await self.repo.update_user_settings(user=user, new_data=new_settings.model_dump())
        await self.repo.commit()

        return UserSettingsResponseSchema(settings=user.settings.settings)

    async def check_user_role(self, user_id, project_id, roles: List[str]):
        # проверяем соответствие роли пользователя
        if not await self.repo.check_user_role(user_id=user_id, project_id=project_id, roles=roles):
            raise UserNotAuthorizedException()

