from fastapi import APIRouter
from fastapi.params import Depends

from src.api.dependencies import get_current_user, get_session
from src.api.schemas.comments_schemas import CreateCommentSchema
from src.api.schemas.tasks_schemas import UpdateTaskSchema
from src.services.comments_services import CommentsServices
from src.services.project_services import ProjectServices
from src.services.tasks_services import TasksService
from src.services.user_services import UserServices

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.delete("/{task_id}")
async def delete_task(task_id: int, user_id: int = Depends(get_current_user), session = Depends(get_session)):
    service = TasksService(session)
    await service.delete_task(task_id=task_id, user_id=user_id)
    return {"Success": True}

@router.patch("/{task_id}")
async def update_task(task_id: int,
                      new_task: UpdateTaskSchema,
                      user_id: int = Depends(get_current_user),
                      session = Depends(get_session)):
    service = TasksService(session)
    await service.update_task(task_id=task_id, new_task=new_task, user_id=user_id)
    return {"Success": True}

@router.post("/{task_id}/comments")
async def create_comment(task_id: int,
                         comment: CreateCommentSchema,
                       user_id: int = Depends(get_current_user),
                       session = Depends(get_session)):
    tasks_service = TasksService(session)
    comm_service = CommentsServices(session)
    await tasks_service.check_user_permission_by_task_id(task_id=task_id, user_id=user_id, roles=["member", "owner"])
    await comm_service.create_comment(task_id=task_id, author_id=user_id, text=comment.text)
    return {"Success": True}