import time

from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from fastapi.responses import JSONResponse
import uuid

from src.core.logger import logger
from src.db.redis_storage import storage


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
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

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, limit: int = 5, window: int = 60):
        super().__init__(app)
        self.limit = limit
        self.window = window
        self.requests = {}

    async def dispatch(self, request: Request, call_next):
        client = request.client.host
        now = time.time()
        self.requests.setdefault(client, [])
        # очищаем устаревшие
        self.requests[client] = [t for t in self.requests[client] if t > now - self.window]
        if len(self.requests[client]) >= self.limit:
            request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
            request.state.request_id = request_id
            return JSONResponse(
                status_code=429,
                content={
                    "error_code": "TOO_MANY_REQUESTS",
                    "detail": "User sent too many requests",
                    "request_id": request_id,
                }
            )

        self.requests[client].append(now)
        return await call_next(request)