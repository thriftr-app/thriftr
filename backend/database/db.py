from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
from starlette import status
from dotenv import load_dotenv
from supabase import create_client, Client
import os

load_dotenv()

def get_db_connection() -> Client: 
    db_url: str = os.environ.get("SUPABASE_DB_URL")
    db_key: str = os.environ.get("SUPABASE_SECRET_KEY")
    if db_url is None or db_key is None:
        raise Exception() 
    db: Client = create_client(db_url, db_key)
    return db

def get_table_by_env(table: str) -> str:
    envs = {'dev', 'test', 'prod'}
    environment = os.environ.get('ENV')
    if environment not in envs:
        raise RuntimeError(f'ENV invalid: {environment}')
    if environment == 'prod':
        return table
    return f'{table}_{environment}' 

router = APIRouter(prefix='/db', tags=['database'])

@router.post('/accounts/lookup', status_code=status.HTTP_200_OK)
async def lookup_user(identifier: str, db: Annotated[Client, Depends(get_db_connection)]):
    if os.environ.get('ENV') not in {'test', 'dev'}:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    users_table = get_table_by_env('users')
    existing_accounts_response = db.table(users_table).select('id').or_(f"username.eq.{identifier},email.eq.{identifier}").limit(1).execute()
    return {'found': len(existing_accounts_response.data) > 0 }

@router.post('/accounts/delete', status_code=status.HTTP_200_OK)
async def delete_account(identifier: str, db:Annotated[Client, Depends(get_db_connection)], status_code=status.HTTP_200_OK):
    users_table = get_table_by_env('users')
    deletion_response = db.table(users_table).delete().or_(f'username.eq.{identifier},email.eq.{identifier}').execute()
    if not deletion_response.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return {'account_identifier': identifier, 'deletion_successful': True}


    
