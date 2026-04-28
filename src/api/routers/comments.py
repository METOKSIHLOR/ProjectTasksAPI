from typing import List

from fastapi import APIRouter, Depends, Header
from uuid import UUID
from src.api.dependencies import CheckUserPerms, get_current_user, get_session
from src.api.schemas.comments_schemas import CommentInfoSchema, CommentUpdateSchema, CreateCommentSchema
from src.services.comments_services import CommentsServices

router = APIRouter(tags=['comments'], prefix='/projects/{project_id}/tasks/{task_id}')

@router.post("/comments", summary="Создать комментарий",
            responses={
                401: {"description": "Пользователь не авторизован"},
                404: {"description": "Задача не была найдена"}
            })
async def create_comment_in_task(project_id: UUID,
                         task_id: UUID,
                         comment: CreateCommentSchema,
                         user_id: UUID = Depends(get_current_user),
                         x_connection_id: str | None = Header(None),
                         session = Depends(get_session)) -> CommentInfoSchema:
    """Создание комментария в таске, если указанная таска находится в указанном проекте"""
    comm_service = CommentsServices(session)
    comment = await comm_service.create_comment(project_id=project_id, task_id=task_id, author_id=user_id, comment=comment, connection_id=x_connection_id)
    return comment

@router.get("/comments", summary="Получить комментарии задачи",
            responses={
                401: {"description": "Пользователь не авторизован"},
                403: {"description": "Пользователь не является участником проекта"},
                404: {"description": "Задача не была найдена"},
            })
async def get_all_comments_in_task(project_id: UUID,
                       task_id: UUID,
                       session = Depends(get_session),
                       _: None = Depends(CheckUserPerms(["member", "owner"]))) -> List[CommentInfoSchema]:
    """Получение всех комментариев конкретной таски, если таска находится в указанном проекте"""
    service = CommentsServices(session)
    comments = await service.get_comments(project_id=project_id, task_id=task_id)
    return comments

@router.patch("/comments/{comment_id}", summary="Обновить комментарий",
            responses={
                401: {"description": "Пользователь не авторизован"},
                403: {"description": "Пользователь не является автором комментария"},
                404: {"description": "Комментарий не был найден | Задача не была найдена"},
            })
async def update_comment(project_id: UUID,
                          task_id: UUID,
                          comment_id: UUID,
                          update: CommentUpdateSchema,
                          user_id: UUID = Depends(get_current_user),
                          session = Depends(get_session)):
    """Обновляет данные о комментарии, если пользователь является его автором и комментарий находится в указанной таске и группе"""
    service = CommentsServices(session)
    await service.update_comment(project_id=project_id, user_id=user_id, text=update.text, comment_id=comment_id, task_id=task_id)
    return {"success": True}

@router.delete("/comments/{comment_id}", summary="Удалить комментарий из таски",
            responses={
                401: {"description": "Пользователь не авторизован"},
                403: {"description": "Пользователь не является автором комментария"},
                404: {"description": "Комментарий не был найден | Задача не была найдена"},
            })
async def delete_comment(project_id: UUID,
                          task_id: UUID,
                          comment_id: UUID,
                          user_id: UUID = Depends(get_current_user),
                         x_connection_id: str | None = Header(None),
                          session = Depends(get_session),):
    """Мягкое удаление комментария из таски (is_deleted=True), если пользователь является его автором или владельцем проекта"""
    service = CommentsServices(session)
    await service.delete_comment(project_id=project_id, comment_id=comment_id, user_id=user_id, task_id=task_id, connection_id=x_connection_id)
    return {"success": True}