from fastapi.param_functions import Form
from pydantic import BaseModel, EmailStr


class TokenModel(BaseModel):
    access_token: str
    token_type: str


class EmailPasswordRequestForm:
    def __init__(
        self,
        email: EmailStr = Form(...),
        password: str = Form(...),
    ):
        self.username = email
        self.password = password