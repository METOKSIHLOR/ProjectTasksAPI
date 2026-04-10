import uuid

from fastapi import HTTPException, status

from src.core.exceptions.base_exception import BaseAPIException

class CommentNotFoundException(BaseAPIException):
    def __init__(self, project_id: uuid.UUID, task_id: uuid.UUID, comment_id: uuid.UUID):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
            error_code="COMMENT_NOT_FOUND",
            extra_data={
                "project_id": str(project_id),
                "task_id": str(task_id),
                "comment_id": str(comment_id)
            }
        )