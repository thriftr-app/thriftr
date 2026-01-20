from pydantic import BaseModel, EmailStr

class User(BaseModel):
    id: int
    username: str
    email: EmailStr
    password: str
    is_active: bool = True

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_active: bool = True