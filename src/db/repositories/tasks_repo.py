from uuid import UUID

from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from src.db.models import Task, Project


class TasksRepository:
    def __init__(self, session):
        self.session = session

    async def create_task(self, task: Task):
        self.session.add(task)
        await self.session.flush()

        await self.session.refresh(task, attribute_names=["assignee"])

        return task

    async def get_task_by_project(self, task_id: UUID, project_id: UUID):
        stmt = (
            select(Task)
            .where(and_(Task.project_id == project_id, Task.id == task_id))
        )
        task = await self.session.execute(stmt)
        return task.scalar_one_or_none()

    async def get_task_by_project_with_owner(self, task_id: UUID, project_id: UUID):
        stmt = (
            select(Task)
            .where(and_(Task.project_id == project_id, Task.id == task_id))
            .options(
                selectinload(Task.assignee),  # подгружаем исполнителя
                selectinload(Task.project).selectinload(Project.owner)  # подгружаем проект и его владельца
            )
        )
        task = await self.session.execute(stmt)
        return task.scalar_one_or_none()


    async def get_project_tasks(self, project_id: UUID):
        stmt = (
            select(Task)
            .where(Task.project_id == project_id)
            .options(selectinload(Task.assignee)).order_by(Task.created_at)
        )

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_task_by_id(self, task_id: UUID):
        stmt = select(Task).where(Task.id == task_id).options(
    selectinload(Task.assignee))
        task = await self.session.execute(stmt)
        return task.scalar_one_or_none()

    async def delete_task(self, task: Task):
        await self.session.delete(task)
        await self.session.flush()
        return task

    async def update_task(self, task: Task, new_task: dict):
        for key, value in new_task.items():
            setattr(task, key, value)

        await self.session.flush()
        return task

    async def commit(self):
        await self.session.commit()
