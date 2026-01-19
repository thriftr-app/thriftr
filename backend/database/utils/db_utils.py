import os 
from supabase import create_client, Client

def get_db_connection() -> Client: 
    db_url: str = os.environ.get("SUPABASE_DB_URL")
    db_key: str = os.environ.get("SUPABASE_SECRET_KEY")
    if db_url is None or db_key is None:
        raise Exception("Database URL or Key not found in environment variables")
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