import uuid

from fastapi import status

from src.core.exceptions.base_exception import BaseAPIException


class TaskNotFoundException(BaseAPIException):
    def __init__(self, project_id: uuid.UUID, task_id: uuid.UUID):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
            error_code="TASK_NOT_FOUND",
            extra_data={
                "project_id": str(project_id),
                "task_id": str(task_id)
            }
        )

class AssigneeNotFoundException(BaseAPIException):
    def __init__(self, project_id: uuid.UUID, task_id: uuid.UUID, assignee_id: uuid.UUID):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignee not found",
            error_code="ASSIGNEE_NOT_FOUND",
            extra_data={
                "project_id": str(project_id),
                "task_id": str(task_id),
                "assignee_id": str(assignee_id)
            }
        )