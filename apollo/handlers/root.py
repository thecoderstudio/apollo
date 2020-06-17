import logging

from apollo.lib.router import SecureRouter
from apollo.lib.schemas.version import VersionSchema
from apollo.lib.version import version

log = logging.getLogger(__name__)
router = SecureRouter()


@router.get("/", response_model=VersionSchema)
def get_root():
    logging.critical('handler')
    return {'version': version}
