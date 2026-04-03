from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from database import SessionLocal
from models import ApiUsageLog

IGNORED_PATHS = {"/docs", "/openapi.json", "/redoc", "/favicon.ico"}

class UsageTrackerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        if request.url.path not in IGNORED_PATHS:
            db = SessionLocal()
            try:
                log = ApiUsageLog(
                    path=request.url.path,
                    method=request.method,
                    status_code=response.status_code,
                )
                db.add(log)
                db.commit()
            finally:
                db.close()

        return response