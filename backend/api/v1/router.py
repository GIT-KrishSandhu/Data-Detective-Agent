from fastapi import APIRouter
from api.v1.endpoints import datasets, agents

api_router = APIRouter()

# Mount endpoints
api_router.include_router(datasets.router, prefix="/datasets", tags=["datasets"])
api_router.include_router(agents.router, prefix="/agents", tags=["agents"])
