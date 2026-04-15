
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
import uuid

from src.core.logger import logger
from src.db.redis_storage import storage


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        user_id = await storage.get(f"session_id:{request.cookies.get("session_id")}")
        # сохраняем данные в state чтоб дальше использовать в обработчиках
        request.state.request_id = request_id
        request.state.user_id = user_id
        logger.info(f"[request:{request_id}] [user:{user_id or 'no-user-id'}] {request.method} {request.url}")
        try:
            response = await call_next(request)
        except Exception as e:
            logger.exception(f"Unhandled exception: {str(e)}")
            raise e
        return response