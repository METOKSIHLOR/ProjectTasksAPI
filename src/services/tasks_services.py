from uuid import UUID

from src.api.websockets.utils import manager
from src.core.exceptions.tasks_exceptions import TaskNotFoundException, AssigneeNotFoundException
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

    async def create_task(self, project_id: UUID, task: CreateTaskSchema, connection_id):
        # проверяем существует ли пользователь с такой почтой
        member = await self.user_serv.get_user_by_email(task.assignee_email)

        # проверяем существует ли такой в проекте такой пользователь
        assignee = await self.project.get_project_member_by_id(
            project_id=project_id, member_id=member.id
        )

        task = await self.repo.create_task(
            Task(
                project_id=project_id,
                title=task.title,
                description=task.description,
                assignee_id=assignee.user_id,
            )
        )

        # маппим данные из вернувшейся модели для дополнительного получения почты исполнителя
        await self.repo.commit()

        await manager.send_to_room(f"project:{project_id}",
                                   {"type": "task_create",
                                    "title": task.title,
                                    "task_id": str(task.id),
                                    "status": task.status,
                                    "assignee_email": task.assignee_email,},
                                   sender_connection_id=connection_id,)

        return TaskInfoSchema(
            id=task.id,
            title=task.title,
            description=task.description,
            status=task.status,
            assignee_email=task.assignee.email,
        )

    async def get_and_check_task_in_this_project(self, task_id: UUID, project_id: UUID):
        """функция проверяет, находится ли указанная таска в указанном проекте, если да - возвращает ее"""

        task = await self.repo.get_task_by_project( # проверяем есть ли такая таска в проекте
            project_id=project_id, task_id=task_id
        )

        if task is None:
            raise TaskNotFoundException(project_id=project_id, task_id=task_id) # если нет - 404 ошибка
        
        return task

    async def get_task_in_project_with_owner(self, task_id: UUID, project_id: UUID):
        """Функция подгружает проект и его владельца в котором находится задача и возвращает результат вместе с ними"""
        task = await self.repo.get_task_by_project_with_owner(
            project_id=project_id, task_id=task_id
        )

        if task is None:
            raise TaskNotFoundException(project_id=project_id, task_id=task_id)

        return task

    async def get_tasks_by_project_id(self, project_id: UUID):
        tasks = await self.repo.get_project_tasks(project_id)
        return tasks

    async def delete_task(self, task_id: UUID, project_id: UUID, connection_id):
        task = await self.get_and_check_task_in_this_project(task_id=task_id, project_id=project_id)
        await self.repo.delete_task(task)

        await manager.send_to_room(f"project:{project_id}",
                                   {"type": "task_delete",
                                    "task_id": str(task.id)},
                                   sender_connection_id=connection_id,)

        await manager.send_to_room(f"task:{task_id}",
                                   {"type": "task_delete"},
                                   sender_connection_id=connection_id,)

        await self.repo.commit()

    async def update_task(
        self, user_id: UUID, task_id: UUID, project_id: UUID, new_task: UpdateTaskSchema, connection_id
    ):
        """функция позволяет исполняющему задачу обновлять только ее статус, а владельцу проекта все поля по желанию"""

        #получаем таску, если она есть в этом проекте 
        task = await self.get_and_check_task_in_this_project(task_id=task_id, project_id=project_id)

        # конвертим Pydantic модель в словарик
        dict_task = new_task.model_dump(exclude_none=True, exclude_unset=True)

        # проверяем является ли пользователь исполнителем таски
        is_assignee = task.assignee_id == user_id

        # проверяем есть ли в запросе на изменение что-то кроме статуса
        is_only_status = set(dict_task) <= {"status"}

        if not (is_only_status and is_assignee):
            # если не исполнитель или обновляется не только статус - проверяем владелец проекта ли пользователь
            await self.user_serv.check_user_role(user_id=user_id, project_id=project_id, roles=["owner"])

        # если владелец обновляет исполнителя задачи
        if "assignee_email" in dict_task:
            # получаем исполнителя, если он есть в этом проекте
            assignee = await self.project.find_project_member_by_email(
                project_id=project_id, member_email=dict_task["assignee_email"]
            )

            if assignee is None:
                raise AssigneeNotFoundException(project_id=project_id,
                                                task_id=task.id,
                                                assignee_id=dict_task["assignee_email"])

            # добавляем айди исполнителя в словарик и убираем оттуда его почту, для обновления она не нужна
            dict_task["assignee_id"] = assignee.user_id
            del dict_task["assignee_email"]

        await self.repo.update_task(task=task, new_task=dict_task)

        await manager.send_to_room(f"project:{project_id}",
                                   {"type": "task_update",
                                    "task_id": str(task.id),
                                    "new_details": dict_task},
                                   sender_connection_id=connection_id,)

        await manager.send_to_room(f"task:{task_id}",
                                   {"type": "task_update",
                                   "new_details": dict_task},
                                   sender_connection_id=connection_id,)

        await self.repo.commit()
        return task
