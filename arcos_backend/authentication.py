from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

EXCLUDED_ENDPOINTS = ['/connect']


class AuthCodeMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, authcode: str):
        super().__init__(app)

        self._authcode = authcode

    async def dispatch(self, request: Request, call_next):
        if (
                self._authcode is not None and
                request.scope['path'] not in EXCLUDED_ENDPOINTS
        ):
            params = request.query_params

            if 'ac' not in params or params['ac'] != self._authcode:
                return Response(status_code=401)

        return await call_next(request)
