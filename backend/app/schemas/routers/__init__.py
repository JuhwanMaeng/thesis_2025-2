from fastapi import APIRouter
from .example_router import router as example_router

router = APIRouter()
router.include_router(example_router, prefix="/examples", tags=["examples"])

