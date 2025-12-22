from fastapi import APIRouter
from starlette import status
router = APIRouter(prefix='/db', tags=['database'])

@router.post('/', status_code=status.HTTP_200_OK)
async def database_root():
    return {"data": "99394949"}
