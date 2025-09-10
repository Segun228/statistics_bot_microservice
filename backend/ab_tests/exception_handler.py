import logging
from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import (
    APIException,
    ValidationError,
    NotAuthenticated,
    AuthenticationFailed,
    PermissionDenied,
    NotFound,
    MethodNotAllowed,
    NotAcceptable,
    UnsupportedMediaType,
    Throttled,
)


def custom_exception_handler(exc, context):
    response = drf_exception_handler(exc, context)

    if response is not None:
        logging.warning(f"Handled exception: {str(exc)}", exc_info=True)
        return response

    if isinstance(exc, ValidationError):
        code = status.HTTP_400_BAD_REQUEST
    elif isinstance(exc, (NotAuthenticated, AuthenticationFailed)):
        code = status.HTTP_401_UNAUTHORIZED
    elif isinstance(exc, PermissionDenied):
        code = status.HTTP_403_FORBIDDEN
    elif isinstance(exc, NotFound):
        code = status.HTTP_404_NOT_FOUND
    elif isinstance(exc, MethodNotAllowed):
        code = status.HTTP_405_METHOD_NOT_ALLOWED
    elif isinstance(exc, NotAcceptable):
        code = status.HTTP_406_NOT_ACCEPTABLE
    elif isinstance(exc, UnsupportedMediaType):
        code = status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
    elif isinstance(exc, Throttled):
        code = status.HTTP_429_TOO_MANY_REQUESTS
    elif isinstance(exc, APIException):
        code = exc.status_code
    else:
        code = status.HTTP_500_INTERNAL_SERVER_ERROR
        logging.error(f"Unhandled exception: {str(exc)}", exc_info=True)

    return Response({"detail": str(exc)}, status=code)