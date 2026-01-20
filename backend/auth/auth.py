from pydantic import BaseModel
from urllib.parse import quote
from starlette import status
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from fastapi import APIRouter, Depends
from fastapi import HTTPException
from backend.auth.models.login_request import LoginRequest
from backend.database.models.user import User
from backend.auth.models.token import Token
from backend.auth.models.register_request import RegisterRequest
from backend.database.utils.db_utils import get_db_connection, get_table_by_env, user_exists, get_user
from typing import Annotated
from supabase import Client
from datetime import datetime, timedelta, timezone
import os

router = APIRouter(prefix='/api/auth', tags=['auth'])

SECRET_KEY = os.environ.get('AUTH_HASH_KEY')
ALGORITHM = os.environ.get('SECRET_ALGORITHM')

crypt_context = CryptContext(schemes=['bcrypt_sha256'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='/api/auth/token')

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    data_to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    data_to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(data_to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.get('/current_user', status_code=status.HTTP_200_OK)
async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)], db: Annotated[Client, Depends(get_db_connection)]) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
    user = get_user(db, identifier=username)
    if user is not None:
        return User.model_validate(user)
    return None

@router.post("/token", status_code=status.HTTP_200_OK)
async def login(request: LoginRequest, db: Annotated[Client, Depends(get_db_connection)]) -> Token:

    user_identifier = request.username if request.username else request.email
    user = get_user(db = db, identifier = user_identifier) 

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    database_password = user.get('password')
    if not crypt_context.verify(request.password, database_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password")

    expiration_delta = timedelta(minutes=30) 
    access_token = create_access_token(data={"sub": user.get('email')}, expires_delta=expiration_delta)
    return Token(access_token=access_token, token_type="bearer")

@router.post("/register", status_code=status.HTTP_200_OK)
async def register_user(request: RegisterRequest, db: Annotated[Client, Depends(get_db_connection)]):
    username = request.username
    email = request.email
    users_table = get_table_by_env('users')

    email_in_use = user_exists(db, email)
    username_in_use = user_exists(db, username)

    if username_in_use:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account with that username already exists")
    if email_in_use:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account with that email already exists")

    hashed_pass = crypt_context.hash(request.password)
    account_creation_res = (db.table(users_table).insert({'username': username, 'password': hashed_pass, 'email': email}).execute())
    if not account_creation_res.data:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Account creation failed, try again later")
    return {"REQUEST": "registration", "user_registered": username, "SUCCESS": True} 
