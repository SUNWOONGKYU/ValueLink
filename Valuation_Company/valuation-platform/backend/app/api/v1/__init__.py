# API v1 module
from fastapi import APIRouter

from app.api.v1.endpoints import investment_tracker, valuation

api_router = APIRouter()

# Investment Tracker endpoints
api_router.include_router(
    investment_tracker.router,
    prefix="/investment-tracker",
    tags=["investment-tracker"]
)

# Valuation endpoints
api_router.include_router(
    valuation.router,
    prefix="/valuation",
    tags=["valuation"]
)
