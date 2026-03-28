from sqlalchemy import select

from src.db.models import Comment


class CommentsRepository:
    def __init__(self, session):
        self.session = session

    async def create_comment(self, comment: Comment):
        self.session.add(comment)
        await self.session.flush()
        return comment

    async def get_comments(self, task_id: int):
        stmt = select(Comment).where(Comment.task_id == task_id)
        comments = await self.session.execute(stmt)
        return comments.scalars().all()

    async def get_comment_by_id(self, comment_id: int):
        stmt = select(Comment).where(Comment.id == comment_id)
        comment = await self.session.execute(stmt)
        return comment.scalar_one_or_none()


    async def is_comment_belong_to_user(self, comment_id: int, user_id: int):
        comment = await self.get_comment_by_id(comment_id)
        if comment is None:
            raise ValueError(f"Comment with id {comment_id} not found")
        if comment.author_id != user_id:
            raise ValueError(f"Comment with id {comment_id} does not belong to user")

        return comment
    async def update_comment(self, comment_id: int, user_id: int, text):
        comment = await self.is_comment_belong_to_user(comment_id, user_id)
        comment.text = text
        await self.session.flush()
        return comment

    async def delete_comment(self, comment_id: int, user_id: int):
        comment = await self.is_comment_belong_to_user(comment_id, user_id)
        await self.session.delete(comment)
        await self.session.flush()
        return comment

    async def commit(self):
        await self.session.commit()

