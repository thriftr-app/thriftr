from fastapi import FastAPI, APIRouter
from backend.database import db
from backend.auth import auth
app = FastAPI()

app.include_router(auth.router)
app.include_router(db.router)
