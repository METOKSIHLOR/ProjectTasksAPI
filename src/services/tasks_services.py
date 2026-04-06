from typing import List

from fastapi import HTTPException

from src.api.schemas.tasks_schemas import (
    CreateTaskSchema,
    UpdateTaskSchema,
    TaskInfoSchema,
)
from src.db.models import Task
from src.db.repositories.tasks_repo import TasksRepository
from src.services.project_services import ProjectServices
from src.services.user_services import UserServices


class TasksService:
    def __init__(self, session):
        self.repo = TasksRepository(session)
        self.project = ProjectServices(session)
        self.user_serv = UserServices(session=session)

    async def create_task(self, project_id: int, task: CreateTaskSchema):
        member = await self.user_serv.get_user_by_email(task.assignee_email)
        assignee = await self.project.get_project_member_by_id(
            project_id=project_id, member_id=member.id
        )

        if assignee is None:
            raise HTTPException(status_code=404, detail="Assignee doesn't exists")

        task = await self.repo.create_task(
            Task(
                project_id=project_id,
                title=task.title,
                description=task.description,
                assignee_id=assignee.user_id,
            )
        )

        await self.repo.commit()
        return TaskInfoSchema(
            id=task.id,
            title=task.title,
            description=task.description,
            status=task.status,
            assignee_email=task.assignee.email,
        )

    async def get_and_check_task_in_this_project(self, task_id, project_id):
        task = await self.repo.get_task_by_project(
            project_id=project_id, task_id=task_id
        )

        if task is None:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return task

    async def get_tasks_by_project_id(self, project_id: int):
        tasks = await self.repo.get_project_tasks(project_id)
        return tasks

    async def delete_task(self, task_id: int, project_id: int):
        task = await self.get_and_check_task_in_this_project(task_id=task_id, project_id=project_id)
        await self.repo.delete_task(task)
        await self.repo.commit()

    async def update_task(
        self, user_id: int, task_id: int, project_id, new_task: UpdateTaskSchema
    ):
        #получаем таску, если она есть в этом проекте 
        task = await self.get_and_check_task_in_this_project(task_id=task_id, project_id=project_id)

        dict_task = new_task.model_dump()
        #проверяем какие поля меняются
        changed_fields = {k: v for k, v in dict_task.items() if v != ""}

        is_assignee = task.assignee_id == user_id
        is_only_status = set(changed_fields) <= {"status"}

        if not (is_only_status and is_assignee):
            await self.user_serv.check_user_role(user_id=user_id, project_id=project_id, roles=["owner"])
                        
        if new_task.assignee_email != "":
            # получаем исполнителя, если он есть в этом проекте
            assignee = await self.project.find_project_member_by_email(
                project_id=project_id, member_email=new_task.assignee_email
            )

            if assignee is None:
                raise HTTPException(status_code=404, detail="Member not found")

            dict_task["assignee_id"] = assignee.user_id
            del dict_task["assignee_email"]

        await self.repo.update_task(task=task, new_task=dict_task)
        await self.repo.commit()
        return task
