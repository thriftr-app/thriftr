from fastapi import FastAPI, APIRouter
import database.db as db
import security.auth as auth
app = FastAPI()

app.include_router(auth.router)
app.include_router(db.router)
