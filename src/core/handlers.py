from fastapi.responses import JSONResponse
from fastapi import Request

from src.core.exceptions.base_exception import BaseAPIException
from src.core.logger import logger

async def exception_handler(request: Request, exc: BaseAPIException):
    request_id = getattr(request.state, "request_id", "no-id") # получаем айди запроса
    logger.warning(f"[{request_id}] {exc.log_message}, Extra: {exc.extra_data}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error_code": exc.error_code,
            "detail": exc.detail,
            "extra_data": exc.extra_data,
            "request_id": request_id,
        }
    )
