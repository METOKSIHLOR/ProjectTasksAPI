from sqlalchemy import select

from src.api.schemas.tasks_schemas import UpdateTaskSchema
from src.db.models import Task

class TasksRepository:
    def __init__(self, session):
        self.session = session

    async def create_task(self, task: Task):
        self.session.add(task)
        await self.session.flush()
        return task

    async def get_project_tasks(self, project_id: int):
        stmt = select(Task).where(Task.project_id == project_id)
        tasks = await self.session.execute(stmt)
        return tasks.scalars().all()

    async def get_task_by_id(self, task_id: int):
        stmt = select(Task).where(Task.id == task_id)
        task = await self.session.execute(stmt)
        return task.scalar_one_or_none()

    async def delete_task(self, task: Task):
        await self.session.delete(task)
        await self.session.flush()
        return task

    async def update_task(self, task: Task, new_task: dict):
        for key, value in new_task.items():
            if value is not "":
                setattr(task, key, value)

        await self.session.flush()
        return task

    async def commit(self):
        await self.session.commit()
