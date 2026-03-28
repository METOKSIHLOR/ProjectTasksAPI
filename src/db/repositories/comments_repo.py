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

    async def commit(self):
        await self.session.commit()

