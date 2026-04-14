import pytest

from src.db.models import Comment, Project, ProjectMember, Task, User
from src.db.repositories.comments_repo import CommentsRepository
from src.db.repositories.project_repo import ProjectRepository
from src.db.repositories.tasks_repo import TasksRepository
from src.db.repositories.user_repo import UserRepository


async def _create_user(repo: UserRepository, email: str, name: str = "User") -> User:
    user = await repo.create_user(User(email=email, name=name, hash_password="hash"))
    await repo.commit()
    return user


@pytest.mark.asyncio
async def test_user_repository_crud_and_roles(db_sessionmaker):
    async with db_sessionmaker() as session:
        user_repo = UserRepository(session)
        project_repo = ProjectRepository(session)

        owner = await _create_user(user_repo, "owner_repo@example.com", "Owner Repo")
        member = await _create_user(user_repo, "member_repo@example.com", "Member Repo")

        project = await project_repo.create_project(
            Project(name="Repo project", owner_id=owner.id)
        )
        await project_repo.add_member(ProjectMember(project_id=project.id, user_id=member.id))
        await project_repo.commit()

        loaded_owner = await user_repo.get_user_by_id(owner.id)
        by_email = await user_repo.get_user_by_email("owner_repo@example.com")
        await user_repo.update_user_profile(loaded_owner, {"name":"Owner Repo Updated"})
        await user_repo.commit()

        projects = await user_repo.get_user_projects(owner.id)
        owner_has_owner_role = await user_repo.check_user_role(owner.id, project.id, ["owner"])
        member_has_owner_role = await user_repo.check_user_role(member.id, project.id, ["owner"])

        assert loaded_owner is not None
        assert by_email is not None
        assert by_email.name == "Owner Repo Updated"
        assert len(projects) == 1
        assert owner_has_owner_role is True
        assert member_has_owner_role is False


@pytest.mark.asyncio
async def test_tasks_repository_crud(db_sessionmaker):
    async with db_sessionmaker() as session:
        user_repo = UserRepository(session)
        project_repo = ProjectRepository(session)
        tasks_repo = TasksRepository(session)

        owner = await _create_user(user_repo, "owner_tasks_repo@example.com")
        project = await project_repo.create_project(Project(name="Tasks repo", owner_id=owner.id))
        await project_repo.commit()

        task = await tasks_repo.create_task(
            Task(
                project_id=project.id,
                title="T1",
                description="D1",
                assignee_id=owner.id,
            )
        )
        await tasks_repo.commit()

        same = await tasks_repo.get_task_by_project(task.id, project.id)
        all_tasks = await tasks_repo.get_project_tasks(project.id)
        await tasks_repo.update_task(task, {"status": "done"})
        await tasks_repo.commit()
        updated = await tasks_repo.get_task_by_id(task.id)
        await tasks_repo.delete_task(task)
        await tasks_repo.commit()
        deleted = await tasks_repo.get_task_by_id(task.id)

        assert same is not None
        assert len(all_tasks) == 1
        assert updated.status == "done"
        assert deleted is None


@pytest.mark.asyncio
async def test_comments_repository_crud(db_sessionmaker):
    async with db_sessionmaker() as session:
        user_repo = UserRepository(session)
        project_repo = ProjectRepository(session)
        tasks_repo = TasksRepository(session)
        comments_repo = CommentsRepository(session)

        owner = await _create_user(user_repo, "owner_comments_repo@example.com")
        project = await project_repo.create_project(Project(name="Comments repo", owner_id=owner.id))
        await project_repo.commit()
        task = await tasks_repo.create_task(
            Task(
                project_id=project.id,
                title="Task",
                description="Desc",
                assignee_id=owner.id,
            )
        )
        await tasks_repo.commit()

        comment = await comments_repo.create_comment(
            Comment(task_id=task.id, author_id=owner.id, text="Initial")
        )
        await comments_repo.commit()

        in_task = await comments_repo.get_comment_in_task(comment.id, task.id)
        by_id = await comments_repo.get_comment_by_id(comment.id)
        all_comments = await comments_repo.get_comments(task.id)
        await comments_repo.update_comment(comment, "Updated")
        await comments_repo.commit()
        updated = await comments_repo.get_comment_by_id(comment.id)
        await comments_repo.delete_comment(comment)
        await comments_repo.commit()
        deleted = await comments_repo.get_comment_by_id(comment.id)

        assert in_task is not None
        assert by_id is not None
        assert len(all_comments) == 1
        assert updated.text == "Updated"
        assert deleted is None
