from pydantic import BaseModel, Field, model_validator, field_validator
from typing import Optional 
import re
class LoginRequest(BaseModel):
    username: Optional[str] = Field(default=None, min_length=3)
    email: Optional[str] = Field(default=None, min_length=3)
    password: str = Field(min_length = 8)

    @model_validator(mode='after')
    def validate_request(self):
        if self.username == None and self.password == None:
            raise ValueError("Username or Email must be provided")
        return self
    
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

