from typing import Callable, Awaitable
import time
import logging
import logging.handlers
import queue
import http

from starlette.exceptions import HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class LoggingMiddleware(BaseHTTPMiddleware):
    _filename: str
    _logger: logging.Logger
    _logging_queue: queue.Queue
    _queue_handler: logging.handlers.QueueHandler
    _queue_listener: logging.handlers.QueueListener
    _handler: logging.FileHandler

    def __init__(self, app, filename: str = "stuff.log"):
        super().__init__(app)

        self._filename = filename

        self._logger = logging.getLogger("arcos_backend")
        self._logger.setLevel(logging.INFO)

        self._logging_queue = queue.Queue()
        self._queue_handler = logging.handlers.QueueHandler(self._logging_queue)
        self._logger.addHandler(self._queue_handler)

        self._handler = logging.FileHandler(self._filename)
        self._handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s - %(message)s"))

        self._queue_listener = logging.handlers.QueueListener(self._logging_queue, self._handler)
        self._queue_listener.start()  # XXX should it be stoppable?

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        callback_time_start = time.perf_counter()

        base_msg = f"{(c := request.client)[0]}:{c[1]} - {request.method} {request.url.path} - "

        def time_taken() -> str:
            nonlocal callback_time_start, callback_time_end

            return f" - {(callback_time_end - callback_time_start) * 1000:.2f}ms"

        try:
            response = await call_next(request)
        except HTTPException as http_exc:
            callback_time_end = time.perf_counter()

            self._logger.warning(base_msg + f"{(code := http_exc.status_code)} {http.HTTPStatus(code).phrase}{f' ({http_exc.detail})' if http_exc.detail is not None else ''}" + time_taken())

            raise http_exc from http_exc.__context__
        except Exception as exc:
            callback_time_end = time.perf_counter()

            self._logger.warning(base_msg + f"500 Internal Server Error ({type(exc).__name__}: {exc})" + time_taken())

            raise exc from exc.__context__
        else:
            callback_time_end = time.perf_counter()

            self._logger.info(base_msg + f"{(code := response.status_code)} {http.HTTPStatus(code).phrase}" + time_taken())

            return response
