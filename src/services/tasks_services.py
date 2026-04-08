from uuid import UUID


from src.api.exceptions.tasks_exceptions import TaskNotFoundException, AssigneeNotFoundException
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

    async def create_task(self, project_id: UUID, task: CreateTaskSchema):
        # проверяем существует ли пользователь с такой почтой
        member = await self.user_serv.get_user_by_email(task.assignee_email)

        # проверяем существует ли такой в проекте такой пользователь
        assignee = await self.project.get_project_member_by_id(
            project_id=project_id, member_id=member.id
        )

        if assignee is None:
            raise AssigneeNotFoundException(project_id=project_id, task_id=task.task_id, assignee_id=task.assignee_id)

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

    async def get_and_check_task_in_this_project(self, task_id: UUID, project_id: UUID):
        task = await self.repo.get_task_by_project(
            project_id=project_id, task_id=task_id
        )

        if task is None:
            raise TaskNotFoundException(project_id=project_id, task_id=task_id)
        
        return task

    async def get_tasks_by_project_id(self, project_id: UUID):
        tasks = await self.repo.get_project_tasks(project_id)
        return tasks

    async def delete_task(self, task_id: UUID, project_id: UUID):
        task = await self.get_and_check_task_in_this_project(task_id=task_id, project_id=project_id)
        await self.repo.delete_task(task)
        await self.repo.commit()

    async def update_task(
        self, user_id: UUID, task_id: UUID, project_id: UUID, new_task: UpdateTaskSchema
    ):
        #получаем таску, если она есть в этом проекте 
        task = await self.get_and_check_task_in_this_project(task_id=task_id, project_id=project_id)

        dict_task = new_task.model_dump(exclude_none=True, exclude_unset=True)

        is_assignee = task.assignee_id == user_id
        is_only_status = set(dict_task) <= {"status"}

        if not (is_only_status and is_assignee):
            await self.user_serv.check_user_role(user_id=user_id, project_id=project_id, roles=["owner"])
                        
        if "assignee_email" in dict_task:
            # получаем исполнителя, если он есть в этом проекте
            assignee = await self.project.find_project_member_by_email(
                project_id=project_id, member_email=dict_task["assignee_email"]
            )

            if assignee is None:
                raise AssigneeNotFoundException(project_id=project_id,
                                                task_id=task.id,
                                                assignee_id=dict_task["assignee_email"])

            dict_task["assignee_id"] = assignee.user_id
            del dict_task["assignee_email"]

        await self.repo.update_task(task=task, new_task=dict_task)
        await self.repo.commit()
        return task
