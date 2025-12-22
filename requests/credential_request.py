from pydantic import Field, BaseModel

class CredentialRequest(BaseModel):
    username: str = Field(min_length=3)
    email: str = Field(min_length=3)

class CredentialResponse(BaseModel):
    user_id: int
    username: str
    auth_token: str
    premium_user: bool
