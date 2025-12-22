from fastapi import FastAPI

app = FastAPI()

@app.get('/')
async def root():
    return {"message": "Hello World!"}

@app.get('/print_number')
async def print_user_num(num: int):
    return {"number": num}
