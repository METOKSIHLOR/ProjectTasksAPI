from sqlalchemy import select, and_

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
        return comment.scalar_one_or_none()

    async def get_comment_in_task(self, comment_id: int, task_id: int):
        stmt = select(Comment).where(and_(Comment.task_id == task_id, Comment.id == comment_id))
        comment = await self.session.execute(stmt)
        return comment.scalar_one_or_none()

    async def update_comment(self, comment: Comment, text):
        comment.text = text
        await self.session.flush()
        return comment

    async def delete_comment(self, comment: Comment):
        await self.session.delete(comment)
        await self.session.flush()
        return comment

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()

