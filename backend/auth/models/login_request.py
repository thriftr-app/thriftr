from pydantic import BaseModel, Field, model_validator, field_validator, EmailStr
from typing import Optional 
import re
class LoginRequest(BaseModel):
    username: Optional[str] = Field(default=None, min_length=3)
    email: Optional[EmailStr] = None 
    password: str = Field(min_length = 8)

    @model_validator(mode='after')
    def validate_request(self):
        if self.username == None and self.email == None:
            raise ValueError("Username or Email must be provided")
        return self
    
    @field_validator("username")
    @classmethod
    def validate_username(cls, username: str | None) -> str | None:
        if username is None:
            return None
        if not re.fullmatch(r"[A-Za-z0-9_]+", username):
            raise ValueError("Username can only contain letters, numbers, and underscores")

        if username.startswith("_") or username.endswith("_"):
            raise ValueError("Username cannot start or end with '_'")

        if "__" in username:
            raise ValueError("Username cannot contain consecutive underscores")

        return username

    @field_validator('password')
    @classmethod
    def validate_password(cls, password:str) -> str:
        if not re.search(r"[A-Z]", password):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", password):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"[0-9]", password):
            raise ValueError("Password must contain at least one number")
        if not re.search(r"[^A-Za-z0-9]", password):
            raise ValueError("Password must contain at least one special character")
        return password

