"""
Pydantic schemas for Valuation Platform API

5가지 평가법:
- DCF평가법 (dcf)
- 상대가치평가법 (relative)
- 자산가치평가법 (asset)
- 본질가치평가법 (capital_market_law)
- 상증세법평가법 (inheritance_tax_law)
"""

from .common import *
from .project import *
from .document import *
from .extraction import *
from .valuation import *
from .approval import *
from .draft import *
from .report import *

__all__ = [
    # Common
    "CompanyInfo",
    "ContactInfo",
    "ValuationInfo",
    "ErrorResponse",

    # Project
    "ProjectCreateRequest",
    "ProjectCreateResponse",
    "QuoteRequest",
    "QuoteResponse",
    "NegotiationRequest",
    "NegotiationResponse",
    "ApprovalRequest",
    "ApprovalResponse",

    # Document
    "DocumentUploadResponse",
    "UploadProgress",

    # Extraction
    "ExtractionRequest",
    "ExtractionResponse",
    "AutoCollectResponse",

    # Valuation
    "CalculationRequest",
    "CalculationResponse",
    "ValuationResult",
    "IntegratedResult",
    "PreviewResponse",
    "SimulationRequest",
    "SimulationResponse",

    # Approval
    "ApprovalPoint",
    "ApprovalPointsResponse",
    "ApprovalDecisionRequest",
    "ApprovalDecisionResponse",

    # Draft
    "DraftRequest",
    "DraftResponse",
    "RevisionRequest",
    "RevisionResponse",

    # Report
    "FinalizeRequest",
    "FinalizeResponse",
    "ReportRequest",
    "ReportResponse",
]
