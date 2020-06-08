import json

from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from apollo import app


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    error = {'detail': []}
    for error_object in json.loads(exc.json()):
        error['detail'].append(
            {
                error_object['loc'][-1]: {
                    'msg': error_object['msg'],
                    'type': error_object['type'],
                    'errors': error_object['ctx']
                }
            }
        )

    return JSONResponse(
        status_code=400,
        content=jsonable_encoder(error)
    )
