from typing import List

from fastapi import APIRouter, Depends

from src.api.dependencies import get_current_user, get_session
from src.api.schemas.comments_schemas import CommentInfoSchema, CommentUpdateSchema, CreateCommentSchema
from src.services.comments_services import CommentsServices

router = APIRouter(tags=['comments'], prefix='/projects/{project_id}/tasks/{task_id}')

@router.post("/comments", summary="Создать комментарий")
async def create_comment_in_task(project_id: int,
                         task_id: int,
                         comment: CreateCommentSchema,
                       user_id: int = Depends(get_current_user),
                       session = Depends(get_session)):
    """Создание комментария в таске, если указанная таска находится в указанном проекте"""
    comm_service = CommentsServices(session)
    await comm_service.create_comment(project_id=project_id, task_id=task_id, author_id=user_id, text=comment.text)
    return {"success": True}

@router.get("/comments", summary="Получить комментарии проекта")
async def get_all_comments_in_task(project_id: int,
                       task_id: int,
                       user_id: int = Depends(get_current_user),
                       session = Depends(get_session)) -> List[CommentInfoSchema]:
    """Получение всех комментариев конкретной таски, если таска находится в указанном проекте"""
    service = CommentsServices(session)
    comments = await service.get_comments(project_id=project_id, task_id=task_id, user_id=user_id)
    return comments

@router.patch("/comments/{comment_id}", summary="Обновить комментарий")
async def update_comment(project_id: int,
                          task_id: int,
                          comment_id: int,
                          update: CommentUpdateSchema,
                          user_id: int = Depends(get_current_user),
                          session = Depends(get_session)):
    """Обновляет данные о комментарии, если пользователь является его автором и комментарий находится в указанной таске и группе"""
    service = CommentsServices(session)
    await service.update_comment(project_id=project_id, user_id=user_id, text=update.text, comment_id=comment_id, task_id=task_id)
    return {"success": True}

@router.delete("/comments/{comment_id}", summary="Удалить комментарий из таски")
async def delete_comment(project_id: int,
                          task_id: int,
                          comment_id: int,
                          user_id: int = Depends(get_current_user),
                          session = Depends(get_session)):
    """Удаление комментария из таски, если пользователь является его автором"""
    service = CommentsServices(session)
    await service.delete_comment(project_id=project_id, comment_id=comment_id, user_id=user_id, task_id=task_id)
    return {"Success": True}