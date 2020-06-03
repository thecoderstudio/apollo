from fastapi import APIRouter

from apollo.lib.schemas.version import VersionSchema
from apollo.lib.version import version

router = APIRouter()


@router.get("/", response_model=VersionSchema)
def get_root():
    return {'version': version}