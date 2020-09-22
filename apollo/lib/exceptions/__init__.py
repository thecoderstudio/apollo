from fastapi import HTTPException as FastAPIHTTPException

class HTTPException(FastAPIHTTPException):
    def __str__(self):
        return self.detail

class ValidationError(Exception):
    def __init__(self, errors: str):
        self.errors = errors