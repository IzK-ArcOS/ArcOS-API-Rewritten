from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class AuthCodeMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, authcode: str):
        super().__init__(app)

        self._authcode = authcode

    async def dispatch(self, request: Request, call_next):
        if self._authcode is None:
            return await call_next(request)

        params = request.query_params

        if 'ac' not in params:
            return Response(status_code=401)

        if params['ac'] != self._authcode:
            return Response(status_code=403)

        return await call_next(request)
