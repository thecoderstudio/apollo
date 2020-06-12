from pydantic import BaseModel, constr


class LoginSchema(BaseModel):
    username: constr(strip_whitespace=True)
    password: constr(strip_whitespace=True)
