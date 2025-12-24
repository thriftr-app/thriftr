from pydantic import BaseModel
from starlette import status
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from fastapi import APIRouter
from backend.models.login_request import LoginRequest
import os

router = APIRouter(prefix='/auth', tags=['auth'])

SECRET_KEY = os.environ.get('AUTH_HASH_KEY')
ALGORITHM = os.environ.get('SECRET_ALGORITHM')

crypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

class Token(BaseModel):
    token: str
    token_type: str
     
@router.post("/", status_code=status.HTTP_200_OK)
async def auth_base():
    return {"auth": "auth_base"}

@router.post("/login", status_code=status.HTTP_200_OK)
async def login(request: LoginRequest):
    return {"login": "request received"}

@router.post("/register", status_code=status.HTTP_200_OK)
async def register_user():
    pass
