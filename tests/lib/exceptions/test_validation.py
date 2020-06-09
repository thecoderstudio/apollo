import json

import pytest
from pydantic import ValidationError
from pydantic import BaseModel, constr

from apollo.lib.exceptions.validation import validation_exception_handler


class Model(BaseModel):
    x: int
    y: constr(min_length=2)


def validation_exception_handler_all_fields():
    with pytest.raises(ValidationError) as e_info:
        Model(x=1, y='x')

    exception = e_info.value
    response = validation_exception_handler(None, exception)

    assert response.status_code == 400
    error_body = json.loads(response.body)['y']
    assert error_body['msg'] == 'ensure this value has at least 2 characters'
    assert error_body['type'] == 'value_error.any_str.min_length'
    assert error_body['errors'] == {'limit_value': 2}


def validation_exception_handler_no_errors_field():
    with pytest.raises(ValidationError) as e_info:
        Model(y='xxx')

    exception = e_info.value
    response = validation_exception_handler(None, exception)

    error_body = json.loads(response.body)['y']
    assert 'errors' not in error_body


def validation_exception_handler_two_errors():
    with pytest.raises(ValidationError) as e_info:
        Model(x='1', y='x')

    exception = e_info.value
    response = validation_exception_handler(None, exception)

    assert len(json.loads(response.body)) == 2
