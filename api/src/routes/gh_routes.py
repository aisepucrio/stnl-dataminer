from fastapi import APIRouter
from src.controllers.gh_controller import router as github_controller

github_router = APIRouter()
github_router.include_router(github_controller)
