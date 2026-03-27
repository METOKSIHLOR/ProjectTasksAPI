from fastapi import HTTPException
from sqlalchemy import select

from src.api.schemas.tasksSchemas import CreateTaskSchema
from src.db.models import Task
from src.db.repositories.tasksRepo import TasksRepository
from src.services.userServices import UserServices


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

    async def get_tasks_by_project_id(self, project_id: int):
        tasks = await self.repo.get_project_tasks(project_id)
        await self.repo.commit()
        return tasks.scalars().all()


    async def delete_task(self, user_id: int, task_id: int):
        user_serv = UserServices(session=self.repo.session)
        task = await self.repo.get_task_by_id(task_id)

        if task is None:
            raise HTTPException(status_code=404, detail="Task not found")

        await user_serv.check_user_role(user_id=user_id, project_id=task.project_id, roles=['owner'])

        result = await self.repo.delete_task(task)

        await self.repo.commit()