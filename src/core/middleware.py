from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
import uuid
from src.core.logger import logger

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id # сохраняем в state чтоб дальше использовать в обработчиках
        logger.info(f"[{request_id}] {request.method} {request.url}")
        try:
            response = await call_next(request)
        except Exception as e:
            logger.exception(f"Unhandled exception: {str(e)}")
            raise e
        return response