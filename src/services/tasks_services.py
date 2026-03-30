from typing import List

from fastapi import HTTPException

from src.api.schemas.tasks_schemas import CreateTaskSchema, UpdateTaskSchema
from src.db.models import Task
from src.db.repositories.tasks_repo import TasksRepository
from src.services.project_services import ProjectServices
from src.services.user_services import UserServices


class TasksService:
    def __init__(self, session):
        self.repo = TasksRepository(session)
        self.project = ProjectServices(session)

    async def create_task(self, project_id: int, user_id: int, task: CreateTaskSchema):
       await self.project.get_project_and_check_user_permission_by_project_id(project_id=project_id, user_id=user_id,
                                                                              roles=["owner"])
       assignee = await self.project.get_project_member_by_id(project_id=project_id, member_id=task.assignee_id)

       if assignee is None:
           raise HTTPException(status_code=404, detail="Assignee doesn't exists")

       task = await self.repo.create_task(Task(
            project_id=project_id,
            title=task.title,
            description=task.description,
            assignee_id=assignee.user_id,
        ))

       await self.repo.commit()
       return task

    async def check_task_in_this_project(self, task_id, project_id):
        task = await self.repo.get_task_by_project(project_id=project_id, task_id=task_id)
        if task is None:
            raise HTTPException(status_code=404, detail="Task not found")

    async def get_task_check_user_permission_by_task_id(self, project_id: int, task_id: int, user_id: int, roles: List[str]):
        await self.check_task_in_this_project(task_id=task_id, project_id=project_id)
        task = await self.repo.get_task_by_id(task_id)
        user_serv = UserServices(self.repo.session)
        if task is None:
            raise HTTPException(status_code=404, detail="Task not found")

        await user_serv.check_user_role(user_id=user_id, project_id=task.project_id, roles=roles)

        return task

    async def get_tasks_by_project_id(self, project_id: int, user_id: int):
        await self.project.get_project_and_check_user_permission_by_project_id(project_id=project_id, user_id=user_id,
                                                                               roles=["member", "owner"])
        tasks = await self.repo.get_project_tasks(project_id)
        return tasks


    async def delete_task(self, user_id: int, task_id: int, project_id: int):
        task = await self.get_task_check_user_permission_by_task_id(project_id=project_id, task_id=task_id, user_id=user_id, roles=["owner"])
        await self.repo.delete_task(task)
        await self.repo.commit()

    async def update_task(self, user_id: int, task_id: int, project_id, new_task: UpdateTaskSchema):
        task = await self.get_task_check_user_permission_by_task_id(project_id=project_id, task_id=task_id, user_id=user_id, roles=["owner"])
        await self.repo.update_task(task=task, new_task=new_task.model_dump(exclude_unset=True))
        await self.repo.commit()
        return task