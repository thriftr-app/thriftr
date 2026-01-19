from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
from starlette import status
from backend.database.utils.db_utils import get_db_connection, get_table_by_env
from supabase import Client
from dotenv import load_dotenv
import os

load_dotenv()

router = APIRouter(prefix='/api/db', tags=['database'])

@router.get('/accounts/lookup', status_code=status.HTTP_200_OK)
async def lookup_user(identifier: str, db: Annotated[Client, Depends(get_db_connection)]):
    if os.environ.get('ENV') not in {'test', 'dev'}:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    users_table = get_table_by_env('users')
    existing_accounts_response = db.table(users_table).select('id').or_(f"username.eq.{identifier},email.eq.{identifier}").limit(1).execute()
    return {'found': len(existing_accounts_response.data) > 0 }

@router.delete('/accounts/delete', status_code=status.HTTP_200_OK)
async def delete_account(identifier: str, db:Annotated[Client, Depends(get_db_connection)]):
    users_table = get_table_by_env('users')
    deletion_response = db.table(users_table).delete().or_(f'username.eq.{identifier},email.eq.{identifier}').execute()
    if not deletion_response.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return {'account_identifier': identifier, 'deletion_successful': True}


    
