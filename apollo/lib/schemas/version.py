from pydantic import BaseModel


class VersionSchema(BaseModel):
    version: str
