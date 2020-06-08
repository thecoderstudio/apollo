import json

from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from apollo import app


@app.exception_handler(RequestValidationError)
def validation_exception_handler(request, exc):
    new_error = {}
    for error_object in json.loads(exc.json()):
        field = error_object['loc'][-1]
        new_error_body = {
            'msg': error_object['msg'],
            'type': error_object['type'],
        }
        if 'ctx' in error_object:
            new_error_body['errors'] = error_object['ctx']

        new_error[field] = new_error_body

    return JSONResponse(
        status_code=400,
        content=jsonable_encoder(new_error)
    )
