from pydantic import BaseModel, Field, model_validator, field_validator
from typing import Optional 
import re
class LoginRequest(BaseModel):
    username: Optional[str] = Field(default=None, min_length=3)
    email: Optional[str] = Field(default=None, min_length=3)
    password: str = Field(min_length = 8)

    @model_validator(mode='after')
    def validate_request(self):
        if self.username == None and self.email == None:
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

    @field_validator("email")
    @classmethod
    def validate_email(cls, email:str) -> str:
        at_index = email.index("@")
        if at_index == -1:
            raise ValueError("Email should have an @ symbol")
        email_name = email[:at_index]
        if len(email_name) < 3:
            raise ValueError("Email username should be at least 3 characters")
        if at_index == len(email)-1 or '.' not in email[at_index+1:] or len(email[at_index+1:]) < 5 or email[-1] == '.':
            raise ValueError("Email domain improperly formatted")
        return email
