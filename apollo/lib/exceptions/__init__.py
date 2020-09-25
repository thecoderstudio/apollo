from fastapi import HTTPException as FastAPIHTTPException


class HTTPException(FastAPIHTTPException):
    def __str__(self):
        return self.detail
