from fastapi import HTTPException


class BaseAPIException(HTTPException):
    def __init__(self, *, status_code: int, detail: str, error_code: str, extra_data: dict | None = None, log_message: str | None = None):
        super().__init__(status_code=status_code, detail=detail)
        self.error_code = error_code
        self.extra_data = extra_data or {}
        self.log_message = log_message or detail