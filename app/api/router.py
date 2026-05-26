from fastapi import APIRouter

from app.api.v1 import funds

api_router = APIRouter()
api_router.include_router(funds.router, prefix="/funds", tags=["funds"])
