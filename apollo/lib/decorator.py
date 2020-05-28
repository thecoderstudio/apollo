import logging

from pydantic import ValidationError

log = logging.getLogger(__name__)

def request_validation(validation_schema):
    def decorate(func):
        def call(self):
            try: 
                #getattr(self.request, data_attr)
                result = validation_schema()
            except ValidationError as e:
                log.debug(e.msg)
                raise ValidationError()
            return func(self, result)
        return call
    return decorate