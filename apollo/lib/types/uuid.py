import logging
import uuid

from sqlalchemy import String
from sqlalchemy.types import TypeDecorator

log = logging.getLogger(__name__)


class UUID(TypeDecorator):
    impl = String

    # unused argumennt for alembic autogenerate
    def __init__(self, length=None):
        self.impl.length = 36
        super().__init__(length=self.impl.length)

    def process_bind_param(self, value, dialect=None):
        if value and isinstance(value, uuid.UUID):
            return str(value)
        elif value and not isinstance(value, uuid.UUID):
            try:
                return str(uuid.UUID(value))
            except:  # noqa E722
                raise ValueError('value %s is not a valid uuid.UUID' % value)
        else:
            return None

    def process_result_value(self, value, dialect=None):
        if not value:
            return None
        try:
            if isinstance(value, str):
                # Sometimes SQLAlchemy can return values padded with spaces.
                # UUIDs should never contain spaces, thus stripping them is
                # safe.
                value = value.strip()
            return uuid.UUID(value)
        except ValueError:
            log.debug("UUID %r not valid", value)
            raise

    def is_mutable(self):
        return False