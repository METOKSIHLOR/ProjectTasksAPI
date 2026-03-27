from src.api.schemas.tasksSchemas import CreateTaskSchema
from src.db.models import Task
from src.db.repositories.tasksRepo import TasksRepository


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