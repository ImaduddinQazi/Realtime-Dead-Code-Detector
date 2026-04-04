import asyncio
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from database import SessionLocal
from models import ApiUsageLog

IGNORED_PATHS = {"/docs", "/openapi.json", "/redoc", "/favicon.ico"}

class UsageTrackerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        if request.url.path not in IGNORED_PATHS:
            # Run DB write in a thread so it doesn't block the async loop
            await asyncio.to_thread(self._log_request, request.url.path, request.method, response.status_code)

        return response

    def _log_request(self, path, method, status_code):
        db = SessionLocal()
        try:
            log = ApiUsageLog(path=path, method=method, status_code=status_code)
            db.add(log)
            db.commit()
        except Exception as e:
            db.rollback()
            print(f"Middleware log error: {e}")
        finally:
            db.close()