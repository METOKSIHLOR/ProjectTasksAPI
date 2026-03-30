from typing import List

from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_current_user, get_session
from src.api.schemas.comments_schemas import CreateCommentSchema, CommentInfoSchema, CommentUpdateSchema
from src.api.schemas.tasks_schemas import UpdateTaskSchema, CreateTaskSchema, TaskInfoSchema
from src.services.comments_services import CommentsServices
from src.services.project_services import ProjectServices
from src.services.tasks_services import TasksService
from src.services.user_services import UserServices

router = APIRouter(prefix="/{project_id}/tasks", tags=["tasks"])

@router.post("")
async def create_project_task(project_id: int,
                              task: CreateTaskSchema,
                            session: AsyncSession = Depends(get_session),
                            user_id: int = Depends(get_current_user)) -> TaskInfoSchema:
    """Ручка создает новую таску в указанном проекте"""
    task_serv = TasksService(session)
    task = await task_serv.create_task(project_id=project_id, user_id=user_id, task=task)
    return task

@router.get("")
async def get_project_tasks(project_id: int,
                            session: AsyncSession = Depends(get_session),
                            user_id = Depends(get_current_user)) -> List[TaskInfoSchema]:
    """Ручка возвращает все таски в этом проекте"""
    task_serv = TasksService(session)
    tasks = await task_serv.get_tasks_by_project_id(project_id=project_id, user_id=user_id)
    return tasks

@router.delete("/{task_id}")
async def delete_task(task_id: int, user_id: int = Depends(get_current_user), session = Depends(get_session)):
    service = TasksService(session)
    await service.delete_task(task_id=task_id, user_id=user_id)
    return {"success": True}

@router.patch("/{task_id}")
async def update_task(task_id: int,
                      new_task: UpdateTaskSchema,
                      user_id: int = Depends(get_current_user),
                      session = Depends(get_session)):
    service = TasksService(session)
    await service.update_task(task_id=task_id, new_task=new_task, user_id=user_id)
    return {"success": True}

