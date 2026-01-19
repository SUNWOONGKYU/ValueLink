from fastapi import APIRouter

from app.api.v1 import api_router as v1_router

router = APIRouter()

# Include v1 API routes
router.include_router(v1_router)

# Future: Additional version routes can be added here
# from app.api.v2 import api_router as v2_router
# router.include_router(v2_router, prefix="/v2")
