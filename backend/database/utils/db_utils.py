import os 
from supabase import create_client, Client

def get_db_connection() -> Client: 
    db_url: str = os.environ.get("SUPABASE_DB_URL")
    db_key: str = os.environ.get("SUPABASE_SECRET_KEY")
    if db_url is None or db_key is None:
        raise Exception("Database URL or Key not found in environment variables")
    db: Client = create_client(db_url, db_key)
    return db

def get_user(db: Client, identifier: str) -> dict | None:
    users_table = get_table_by_env('users')
    response = db.table(users_table).select('id,username,email,password').or_(f"username.eq.{identifier},email.eq.{identifier}").limit(1).execute()
    if len(response.data) == 0:
        return None
    return response.data[0]

def get_user_by_id(db: Client, user_id: int) -> dict | None:
    users_table = get_table_by_env('users')
    response = db.table(users_table).select('id,username,email,password').eq('id', user_id).limit(1).execute()
    if len(response.data) == 0:
        return None
    return response.data[0]

def user_exists(db: Client, identifier: str) -> bool:
    users_table = get_table_by_env('users')
    response = db.table(users_table).select('id').or_(f"username.eq.{identifier},email.eq.{identifier}").limit(1).execute()
    return len(response.data) > 0

def get_table_by_env(table: str) -> str:
    envs = {'dev', 'test', 'prod'}
    environment = os.environ.get('ENV')
    if environment not in envs:
        raise RuntimeError(f'ENV invalid: {environment}')
    if environment == 'prod':
        return table
    return f'{table}_{environment}' 

def delete_user(db: Client, identifier: str) -> bool:
    users_table = get_table_by_env('users')
    response = db.table(users_table).delete().or_(f"username.eq.{identifier},email.eq.{identifier}").execute()
    return len(response.data) > 0
