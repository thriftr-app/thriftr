from pydantic import BaseModel
from urllib.parse import quote
from starlette import status
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from fastapi import APIRouter, Depends
from fastapi import HTTPException
from backend.auth.models.login_request import LoginRequest
from backend.database.models.user import UserResponse 
from backend.auth.models.token import Token
from backend.auth.models.register_request import RegisterRequest
from backend.database.utils.db_utils import get_db_connection, get_table_by_env, user_exists, get_user, get_user_by_id, delete_user
from typing import Annotated
from supabase import Client
from datetime import datetime, timedelta, timezone
import os

router = APIRouter(prefix='/api/auth', tags=['auth'])

SECRET_KEY = os.environ.get('AUTH_HASH_KEY')
ALGORITHM = os.environ.get('SECRET_ALGORITHM')

if SECRET_KEY is None or ALGORITHM is None:
    raise RuntimeError("AUTH_HASH_KEY and SECRET_ALGORITHM must be set in environment")

crypt_context = CryptContext(schemes=['bcrypt_sha256'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='/api/auth/token')

DUMMY_PASSWORD_HASH = "$bcrypt-sha256$v=2,t=2b,r=12$N.b83rO2ds45hzLmXMuZOO$53eZnLaXPEHLPuonMVYv4ur5qbilq0C"

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    data_to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    data_to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(data_to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@router.delete('/current_user', status_code=status.HTTP_200_OK)
async def delete_current_user(token: Annotated[str, Depends(oauth2_bearer)], db: Annotated[Client, Depends(get_db_connection)]):
    credential_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not verify credentials')
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id_str: str = payload.get('sub')
        if user_id_str is None:
            raise credential_exception
        user_id = int(user_id_str)
    except (JWTError, ValueError):
        raise credential_exception

    user = get_user_by_id(db, user_id=user_id)
    if user is None:
        raise credential_exception

    username = user.get('username')
    deleted = delete_user(db, identifier=username)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Account deletion failed')
    
    return {'message': 'Account deleted successfully', 'username': username}

@router.get('/current_user', status_code=status.HTTP_200_OK)
async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)], db: Annotated[Client, Depends(get_db_connection)]) -> UserResponse:
    credential_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id_str: str = payload.get('sub')
        if user_id_str is None:
            raise credential_exception
        user_id = int(user_id_str)
    except (JWTError, ValueError):
        raise credential_exception
    user = get_user_by_id(db, user_id=user_id)
    if user is not None:
        del user['password']
        return UserResponse.model_validate(user)
    raise credential_exception

@router.post("/token", status_code=status.HTTP_200_OK)
async def login(request: LoginRequest, db: Annotated[Client, Depends(get_db_connection)]) -> Token:
    credential_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    user_identifier = request.username if request.username else request.email
    user = get_user(db = db, identifier = user_identifier) 

    if user is None:
        crypt_context.verify(request.password, DUMMY_PASSWORD_HASH)
        raise credential_exception 
    database_password = user.get('password')
    if not crypt_context.verify(request.password, database_password):
        raise credential_exception

    expiration_delta = timedelta(minutes=30) 
    access_token = create_access_token(data={"sub": str(user.get('id'))}, expires_delta=expiration_delta)
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
