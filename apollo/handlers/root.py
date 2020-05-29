from fastapi import APIRouter

from apollo.lib.version import version

router = APIRouter()


@router.get("/")
def get_root():
    return {'version': version}