"""
API v1 router.
"""
from fastapi import APIRouter

from app.interfaces.api.v1.endpoints import users, jobs, applications

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
api_router.include_router(applications.router, prefix="/applications", tags=["applications"]) 