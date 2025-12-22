from fastapi import FastAPI
from requests.credential_request import CredentialRequest
from requests.credential_request import CredentialResponse
app = FastAPI()

@app.get('/')
async def root():
    return {"data": "what Yeah"}

@app.get('/login', response_model=CredentialResponse)
async def login_attempt(request: CredentialRequest):
    return {"user_id": 32,"username": request.username,"auth_token": "kioj3oiv3i4jij1fojoif", "premium_user": False}
