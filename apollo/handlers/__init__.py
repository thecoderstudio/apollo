import logging 

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from apollo.models import save as save_object

log = logging.getLogger(__name__)


def save(obj):
    try:
        obj_copy = save_object(obj)
    except Exception as e:  # noqa 772
        log_critical_and_raise(e)

    return obj_copy

def log_critical_and_raise(e):
    log.critical(e, exc_info=True)
    raise HTTPException(status_code=500, 
        detail='Something went wrong when saving the object.')