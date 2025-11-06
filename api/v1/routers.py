from fastapi import APIRouter
from api.v1.endpoints import level_test, planner

api_router = APIRouter()

api_router.include_router(planner.router, prefix="/planner", tags=["planner"])
api_router.include_router(level_test.router, prefix="/level-test", tags=["level-test"])