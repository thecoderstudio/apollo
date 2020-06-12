from apollo.lib.router import SecureRouter
from apollo.lib.schemas.version import VersionSchema
from apollo.lib.version import version

router = SecureRouter()


@router.get("/", response_model=VersionSchema)
def get_root():
    return {'version': version}
