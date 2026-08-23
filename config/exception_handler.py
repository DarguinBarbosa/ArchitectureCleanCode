from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler

from shared.domain.exceptions import NotFoundError, ValidationError


def _error_response(status_code: int, error_type: str, detail: object) -> Response:
    return Response(
        {"error": {"status": status_code, "type": error_type, "detail": detail}},
        status=status_code,
    )


def custom_exception_handler(exc: Exception, context: dict) -> Response | None:
    if isinstance(exc, NotFoundError):
        return _error_response(
            status.HTTP_404_NOT_FOUND, type(exc).__name__, str(exc)
        )
    if isinstance(exc, ValidationError):
        return _error_response(
            status.HTTP_400_BAD_REQUEST, type(exc).__name__, str(exc)
        )
    response = exception_handler(exc, context)
    if response is not None:
        return _error_response(response.status_code, type(exc).__name__, response.data)
    return None
