from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from fastapi import APIRouter

router = APIRouter(prefix='/auth', tags=['auth'])

@router.post("/", status_code=status.HTTP_200_OK)
async def auth_base():
    return {"auth": "auth_base"}
