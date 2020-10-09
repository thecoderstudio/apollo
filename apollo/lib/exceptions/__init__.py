from fastapi import HTTPException as FastAPIHTTPException
from pydantic import ValidationError
from pydantic.errors import PydanticValueError
from pydantic.error_wrappers import ErrorWrapper


class HTTPException(FastAPIHTTPException):
    def __str__(self):
        return self.detail


class PydanticValidationError(ValidationError):

    def __init__(self, message, location, schemaObject, *args, **kwargs):
        super().__init__(
            [ErrorWrapper(PydanticError(message), location)],
            schemaObject,
            *args,
            **kwargs
        )


class PydanticError(PydanticValueError):
    msg_template: str

    def __init__(self, message, *args, **kwargs):
        self.msg_template = message
