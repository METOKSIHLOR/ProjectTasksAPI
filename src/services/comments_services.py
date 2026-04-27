from uuid import UUID

from src.api.routers.websockets import manager
from src.core.exceptions.comments_exceptions import CommentNotFoundException
from src.core.exceptions.users_exceptions import UserNotAuthenticatedException
from src.services.user_services import UserServices
from src.api.schemas.comments_schemas import CommentInfoSchema, CreateCommentSchema
from src.db.models import Comment
from src.db.repositories.comments_repo import CommentsRepository
from src.services.tasks_services import TasksService


class CommentsServices:
    def __init__(self, session):
        self.repo = CommentsRepository(session)
        self.tasks_service = TasksService(session)

    async def create_comment(
        self, project_id: UUID, task_id: UUID, author_id: UUID, comment: CreateCommentSchema, connection_id
    ):
        await self.tasks_service.get_and_check_task_in_this_project(project_id=project_id, task_id=task_id)
        comment = Comment(task_id=task_id, author_id=author_id, text=comment.text, replied_to=comment.replied_to)

        if comment.replied_to is not None:
            # проверяем существует ли такой комментарий в таске, чтоб на него отвечать
            await self.get_comment_belong_to_task(project_id=project_id, task_id=task_id, comment_id=comment.replied_to)

        created_comment = await self.repo.create_comment(comment)

        await self.repo.commit()
        await self.repo.session.refresh(comment, attribute_names=["author"])

        await manager.send_to_room(f"task:{task_id}",
                                   {"type": "comment_create",
                                    "comment_id": str(created_comment.id),
                                    "text": comment.text,
                                    "replied_to": str(comment.replied_to) if comment.replied_to is not None else None,
                                    "author_name": comment.author.name,
                                    "author_email": comment.author.email,
                                    "created_at": comment.created_at.isoformat(),},
                                   sender_connection_id=connection_id)

        return comment

    async def get_comments(self, project_id: UUID, task_id: UUID):
        """функция возвращает все комментарии в таске"""

        #проверяем есть ли такая таска в проекте вообще
        await self.tasks_service.get_and_check_task_in_this_project(task_id=task_id, project_id=project_id)

        # возвращаем список комментов
        comments = await self.repo.get_comments(task_id=task_id)

        # маппим модели и получаем дополнительные поля
        return [
            CommentInfoSchema(
                id=comment.id,
                text=comment.text,
                author_email=comment.author.email,
                author_name=comment.author.name,
                replied_to=comment.replied_to if not comment.is_reply_deleted else "deleted",
                created_at=comment.created_at,
            )
            for comment in comments
        ]

    async def update_comment(
        self, project_id: UUID, comment_id: UUID, task_id: UUID, user_id: UUID, text: str, connection_id
    ):
        # проверяем находится ли такой комментарий в указанной задаче
        comment = await self.get_comment_belong_to_task(
            project_id=project_id, comment_id=comment_id, task_id=task_id
        )

        # если пользователь не является автором комментария
        if str(comment.author_id) != str(user_id):
            raise UserNotAuthenticatedException()

        await self.repo.update_comment(comment=comment, text=text)
        await self.repo.commit()

        await manager.send_to_room(f"task:{task_id}",
                                   {"type": "comment_update",
                                    "task_id": str(task_id),
                                    "comment_id": str(comment_id),
                                    "new_text": text,},
                                   sender_connection_id=connection_id)

        return comment

    async def delete_comment(
        self, project_id: UUID, comment_id: UUID, task_id: UUID, user_id: UUID, connection_id
    ):
        user_serv = UserServices(session=self.repo.session)
        comment = await self.get_comment_belong_to_task( # принадлежит ли комментарий указанной таске
            project_id=project_id, comment_id=comment_id, task_id=task_id
        )
        

        if comment.author_id != user_id: # если пользователь не является автором комментария, проверяем является ли он владельцем проекта
            await user_serv.check_user_role(project_id=project_id, user_id=user_id, roles=["owner"])

        await self.repo.delete_comment(comment)

        await self.repo.commit()

        await manager.send_to_room(f"task:{task_id}",
                                   {"type": "comment_delete",
                                    "task_id": str(task_id),
                                    "comment_id": str(comment_id),},
                                   sender_connection_id=connection_id)
        return comment

    async def get_comment_belong_to_task(
        self, comment_id: UUID, task_id: UUID, project_id: UUID
    ):
        """Функция проверяет, находится ли такой комментарий в таске"""
        await self.tasks_service.get_and_check_task_in_this_project(
            task_id=task_id, project_id=project_id
        )
        comment = await self.repo.get_comment_in_task(
            comment_id=comment_id, task_id=task_id
        )

        if comment is None:
            raise CommentNotFoundException(project_id=project_id, task_id=task_id, comment_id=comment_id)

        return comment
