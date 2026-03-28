from typing import List

from fastapi import HTTPException
from sqlalchemy import select

from src.api.schemas.tasks_schemas import CreateTaskSchema, UpdateTaskSchema
from src.db.models import Task
from src.db.repositories.tasks_repo import TasksRepository
from src.services.user_services import UserServices


class TasksService:
    def __init__(self, session):
        self.repo = TasksRepository(session)

    async def create_task(self, project_id: int, task: CreateTaskSchema):
       task = await self.repo.create_task(Task(
            project_id=project_id,
            title=task.title,
            description=task.description,
            assignee_id=task.assignee_id,
        ))

       await self.repo.commit()
       return task

    async def check_user_permission_by_task_id(self, task_id: int, user_id: int, roles: List[str]):
        task = await self.repo.get_task_by_id(task_id)
        user_serv = UserServices(self.repo.session)
        if task is None:
            raise HTTPException(status_code=404, detail="Task not found")

        await user_serv.check_user_role(user_id=user_id, project_id=task.project_id, roles=roles)

        return task

    async def get_tasks_by_project_id(self, project_id: int):
        tasks = await self.repo.get_project_tasks(project_id)
        await self.repo.commit()
        return tasks.scalars().all()


    async def delete_task(self, user_id: int, task_id: int):
        task = await self.check_user_permission_by_task_id(task_id=task_id, user_id=user_id, roles=["owner"])
        await self.repo.delete_task(task)
        await self.repo.commit()

    async def update_task(self, user_id: int, task_id: int, new_task: UpdateTaskSchema):
        await self.check_user_permission_by_task_id(task_id=task_id, user_id=user_id, roles=["owner"])
        updated = await self.repo.update_task(task_id, new_task.model_dump(exclude_unset=True))
        await self.repo.commit()
        return updated