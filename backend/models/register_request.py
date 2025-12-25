from pydantic import BaseModel, Field, field_validator, EmailStr
import re

class RegisterRequest(BaseModel):
    username: str = Field(min_length=3)
    email: EmailStr
    password: str = Field(min_length = 8)

    
    @field_validator("username")
    @classmethod
    def validate_username(cls, username: str) -> str:
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

