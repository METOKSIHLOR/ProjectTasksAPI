import uuid

from fastapi import HTTPException, status


class BaseCommentException(HTTPException):
    def __init__(
        self,
        *,
        status_code: int,
        detail: str,
        error_code: str,
        extra_data: dict | None = None,
        log_message: str | None = None,
    ):
        super().__init__(status_code=status_code, detail=detail)
        self.error_code = error_code
        self.extra_data = extra_data or {}
        self.log_message = log_message or detail

class CommentNotFoundException(BaseCommentException):
    def __init__(self, project_id: uuid.UUID, task_id: uuid.UUID, comment_id: uuid.UUID):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
            error_code="COMMENT_NOT_FOUND",
            extra_data={
                "project_id": project_id,
                "task_id": task_id,
                "comment_id": comment_id
            }
        )