from pydantic import BaseModel
from urllib.parse import quote
from starlette import status
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from fastapi import APIRouter, Depends
from fastapi import HTTPException
from backend.models.login_request import LoginRequest
from backend.models.register_request import RegisterRequest
from backend.database.db import get_db_connection, get_table_by_env
from typing import Annotated
from supabase import Client
import os

router = APIRouter(prefix='/api/auth', tags=['auth'])

SECRET_KEY = os.environ.get('AUTH_HASH_KEY')
ALGORITHM = os.environ.get('SECRET_ALGORITHM')

crypt_context = CryptContext(schemes=['bcrypt_sha256'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

class Token(BaseModel):
    token: str
    token_type: str


@router.post("/login", status_code=status.HTTP_200_OK)
async def login(request: LoginRequest):
    return {"login": "request received"}

@router.post("/register", status_code=status.HTTP_200_OK)
async def register_user(request: RegisterRequest, db: Annotated[Client, Depends(get_db_connection)]):
    username = request.username
    email = request.email
    users_table = get_table_by_env('users')
    existing_accounts_response = db.table(users_table).select('username,email').or_(f"username.eq.{username},email.eq.{email}").limit(1).execute()
    existing_accounts = existing_accounts_response.data

    if existing_accounts:
        existing_username = existing_accounts[0]['username']
        if existing_username == username:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account with that username already exists")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account with that email already exists")

    hashed_pass = crypt_context.hash(request.password)
    account_creation_res = (db.table(users_table).insert({'username': username, 'password': hashed_pass, 'email': email}).execute())
    if not account_creation_res.data:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Account creation failed, try again later")
    return {"REQUEST": "registration", "user_registered": username, "SUCESS": True} 

