import pytest

from src.api.authorization.hash import hash_password
from src.core.exceptions.comments_exceptions import CommentNotFoundException
from src.core.exceptions.project_exceptions import ProjectDeleteConflictException, ProjectMemberNotFoundException
from src.core.exceptions.tasks_exceptions import TaskNotFoundException
from src.core.exceptions.users_exceptions import (
    ConflictEmailException,
    InvalidUserCredentialsException,
    UserNotAuthenticatedException,
)
from src.api.schemas.comments_schemas import CreateCommentSchema
from src.api.schemas.project_schemas import CreateProjectSchema
from src.api.schemas.tasks_schemas import CreateTaskSchema, UpdateTaskSchema
from src.api.schemas.user_schemas import UserCredsSchema, UserRegistrationSchema
from src.db.models import User
from src.db.redis_storage import storage
from src.db.repositories.user_repo import UserRepository
from src.services.comments_services import CommentsServices
from src.services.project_services import ProjectServices
from src.services.tasks_services import TasksService
from src.services.user_services import UserServices


class _FakeStorage:
    def __init__(self):
        self.data: dict[str, str] = {}

    async def set(self, key: str, value: str, ex: int | None = None):
        self.data[key] = value

    async def get(self, key: str):
        return self.data.get(key)

    async def delete(self, key: str):
        self.data.pop(key, None)


@pytest.mark.asyncio
async def test_user_service_register_and_auth(db_sessionmaker, monkeypatch):
    async with db_sessionmaker() as session:
        service = UserServices(session)
        fake_storage = _FakeStorage()
        monkeypatch.setattr(storage, "set", fake_storage.set)
        monkeypatch.setattr(storage, "get", fake_storage.get)

        user = await service.register(
            UserRegistrationSchema(
                name="Service User", email="service_user@example.com", password="secret123"
            )
        )
        session_id = await service.auth(
            UserCredsSchema(email="service_user@example.com", password="secret123")
        )

        stored_user_id = await fake_storage.get(f"session_id:{session_id}")

        assert user.email == "service_user@example.com"
        assert stored_user_id == str(user.id)


@pytest.mark.asyncio
async def test_user_service_register_duplicate_and_invalid_auth(db_sessionmaker):
    async with db_sessionmaker() as session:
        service = UserServices(session)
        await service.register(
            UserRegistrationSchema(
                name="Service User", email="dup_service@example.com", password="secret123"
            )
        )

        with pytest.raises(ConflictEmailException):
            await service.register(
                UserRegistrationSchema(
                    name="Service User 2", email="dup_service@example.com", password="secret123"
                )
            )

        with pytest.raises(InvalidUserCredentialsException):
            await service.auth(UserCredsSchema(email="dup_service@example.com", password="wrong"))


@pytest.mark.asyncio
async def test_project_service_remove_self_forbidden(db_sessionmaker):
    async with db_sessionmaker() as session:
        user_repo = UserRepository(session)
        owner = await user_repo.create_user(
            User(email="owner_service@example.com", name="Owner", hash_password=hash_password("secret123"))
        )
        await user_repo.commit()

        project_service = ProjectServices(session)
        project = await project_service.create_new_project(
            CreateProjectSchema(name="Service project"), owner.id
        )

        with pytest.raises(ProjectDeleteConflictException):
            await project_service.remove_member(
                project_id=project.id,
                member_email="owner_service@example.com",
                user_id=owner.id,
            )


@pytest.mark.asyncio
async def test_tasks_service_not_found_and_assignee_not_found(db_sessionmaker):
    async with db_sessionmaker() as session:
        user_repo = UserRepository(session)
        owner = await user_repo.create_user(
            User(email="owner_tasks_service@example.com", name="Owner", hash_password=hash_password("secret123"))
        )
        alien = await user_repo.create_user(
            User(email="alien_tasks_service@example.com", name="Alien", hash_password=hash_password("secret123"))
        )
        await user_repo.commit()

        project_service = ProjectServices(session)
        project = await project_service.create_new_project(
            CreateProjectSchema(name="Tasks service"), owner.id
        )

        tasks_service = TasksService(session)
        with pytest.raises(TaskNotFoundException):
            await tasks_service.get_and_check_task_in_this_project(
                task_id=project.id, project_id=project.id
            )

        with pytest.raises(ProjectMemberNotFoundException):
            await tasks_service.create_task(
                project_id=project.id,
                task=CreateTaskSchema(
                    title="Task",
                    description="Desc",
                    assignee_email=alien.email,
                ),
            )


@pytest.mark.asyncio
async def test_comments_service_forbidden_update_and_not_found(db_sessionmaker):
    async with db_sessionmaker() as session:
        user_service = UserServices(session)
        owner = await user_service.register(
            UserRegistrationSchema(name="Owner", email="owner_comments_service@example.com", password="secret123")
        )
        member = await user_service.register(
            UserRegistrationSchema(name="Member", email="member_comments_service@example.com", password="secret123")
        )

        project_service = ProjectServices(session)
        project = await project_service.create_new_project(CreateProjectSchema(name="Comments service"), owner.id)
        await project_service.add_member(member_email=member.email, project_id=project.id)

        tasks_service = TasksService(session)
        task = await tasks_service.create_task(
            project_id=project.id,
            task=CreateTaskSchema(
                title="Task",
                description="Desc",
                assignee_email=owner.email,
            ),
        )

        comments_service = CommentsServices(session)
        comment = await comments_service.create_comment(
            project_id=project.id,
            task_id=task.id,
            author_id=owner.id,
            text=CreateCommentSchema(text="comment").text,
        )

        with pytest.raises(UserNotAuthenticatedException):
            await comments_service.update_comment(
                project_id=project.id,
                comment_id=comment.id,
                task_id=task.id,
                user_id=member.id,
                text="new text",
            )

        with pytest.raises(CommentNotFoundException):
            await comments_service.get_comment_belong_to_task(
                comment_id=project.id,
                task_id=task.id,
                project_id=project.id,
            )


@pytest.mark.asyncio
async def test_tasks_service_owner_can_update_assignee(db_sessionmaker):
    async with db_sessionmaker() as session:
        user_service = UserServices(session)
        owner = await user_service.register(
            UserRegistrationSchema(name="Owner", email="owner_update_service@example.com", password="secret123")
        )
        member = await user_service.register(
            UserRegistrationSchema(name="Member", email="member_update_service@example.com", password="secret123")
        )

        project_service = ProjectServices(session)
        project = await project_service.create_new_project(CreateProjectSchema(name="Update service"), owner.id)
        await project_service.add_member(member_email=member.email, project_id=project.id)

        tasks_service = TasksService(session)
        task = await tasks_service.create_task(
            project_id=project.id,
            task=CreateTaskSchema(
                title="Task",
                description="Desc",
                assignee_email=owner.email,
            ),
        )

        await tasks_service.update_task(
            user_id=owner.id,
            project_id=project.id,
            task_id=task.id,
            new_task=UpdateTaskSchema(assignee_email=member.email),
        )
        updated_task = await tasks_service.get_and_check_task_in_this_project(task.id, project.id)
        assert updated_task.assignee_id == member.id
