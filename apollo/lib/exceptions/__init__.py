from fastapi import HTTPException as FastAPIHTTPException

from pydantic import ValidationError
from pydantic.errors import PydanticValueError
from pydantic.error_wrappers import ErrorWrapper


class HTTPException(FastAPIHTTPException):
    def __str__(self):
        return self.detail


class PydanticValidationError(ValidationError):
