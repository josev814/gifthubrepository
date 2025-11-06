from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from starlette.responses import JSONResponse

ALLOWED_ORIGINS = set([ 'http://localhost:5173' ])

class OriginValidationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        origin = request.headers.get('origin')
        if origin and origin not in ALLOWED_ORIGINS:
            return JSONResponse(status_code=403, content={'detail':'Invalid origin'})
        return await call_next(request)
