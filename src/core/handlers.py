from fastapi.responses import JSONResponse
from fastapi import Request

from src.core.exceptions.base_exception import BaseAPIException
from src.core.logger import logger

async def exception_handler(request: Request, exc: BaseAPIException):
    request_id = getattr(request.state, "request_id", "no-request-id") # получаем айди запроса
    user_id = {"user_id": getattr(request.state, "user_id", "no-user-id")}
    logger.warning(f"[{request_id}] {exc.log_message}, Extra: {user_id | exc.extra_data}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error_code": exc.error_code,
            "detail": exc.detail,
            "extra_data": user_id | exc.extra_data,
            "request_id": request_id,
        }
    )
