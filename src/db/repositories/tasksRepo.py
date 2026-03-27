from sqlalchemy import select

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
        await self.session.flush()
        return tasks

    async def commit(self):
        await self.session.commit()
