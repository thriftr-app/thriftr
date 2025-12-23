from fastapi import APIRouter, Depends
from typing import Annotated
from starlette import status
from dotenv import load_dotenv
from supabase import create_client, Client
import os

load_dotenv()

def get_db_connection() -> Client: 
    db_url: str = os.environ.get("SUPABASE_DB_URL")
    db_key: str = os.environ.get("SUPABASE_SECRET_KEY")
    if db_url == None or db_key == None:
        raise Exception() 
    db: Client = create_client(db_url, db_key)
    return db

router = APIRouter(prefix='/db', tags=['database'])

@router.post('/', status_code=status.HTTP_200_OK)
async def database_root(db: Annotated[Client, Depends(get_db_connection)]):
    data = db.table('clothing-items').select('*').limit(1).execute()
    return {"data": data.data}
