"""
Valuation API Endpoints
평가법별 14단계 프로세스 관리 API

@task Valuation Platform
@description FastAPI endpoints for managing the 14-step valuation process
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import datetime
import logging

from app.db.supabase_client import supabase_client

router = APIRouter()
logger = logging.getLogger(__name__)

# ============================================================
# Constants
# ============================================================

VALID_METHODS = ["dcf", "relative", "intrinsic", "asset", "inheritance_tax"]
VALID_STATUSES = ["not_requested", "pending", "approved", "in_progress", "completed"]
MIN_STEP = 1
MAX_STEP = 14

# ============================================================
# Pydantic Models
# ============================================================

class StartValuationRequest(BaseModel):
    """평가 시작 요청 모델"""
    project_id: str = Field(..., description="프로젝트 ID")
    method: Literal["dcf", "relative", "intrinsic", "asset", "inheritance_tax"] = Field(
        ..., description="평가 방법"
    )

class StartValuationResponse(BaseModel):
    """평가 시작 응답 모델"""
    status: str = Field(..., description="시작 상태")
    project_id: str = Field(..., description="프로젝트 ID")
    method: str = Field(..., description="평가 방법")
    message: str = Field(..., description="응답 메시지")

class ProgressResponse(BaseModel):
    """진행 상황 응답 모델"""
    progress: int = Field(..., ge=0, le=100, description="진행률 (0-100)")
    current_step: int = Field(..., ge=1, le=14, description="현재 단계 (1-14)")
    status: str = Field(..., description="평가 상태")
    message: str = Field(..., description="상태 메시지")

class ResultResponse(BaseModel):
    """평가 결과 응답 모델"""
    valuation_amount: Optional[float] = Field(None, description="평가 금액")
    currency: str = Field(default="KRW", description="통화")
    report_url: Optional[str] = Field(None, description="보고서 URL")
    completed_at: Optional[str] = Field(None, description="완료 시각")

class AdvanceStepRequest(BaseModel):
    """단계 전진 요청 모델"""
    project_id: str = Field(..., description="프로젝트 ID")
    method: Literal["dcf", "relative", "intrinsic", "asset", "inheritance_tax"] = Field(
        ..., description="평가 방법"
    )

class AdvanceStepResponse(BaseModel):
    """단계 전진 응답 모델"""
    status: str = Field(..., description="전진 상태")
    new_step: int = Field(..., ge=1, le=14, description="새 단계 번호")
    message: str = Field(..., description="응답 메시지")

class UpdateStatusRequest(BaseModel):
    """상태 업데이트 요청 모델"""
    project_id: str = Field(..., description="프로젝트 ID")
    method: Literal["dcf", "relative", "intrinsic", "asset", "inheritance_tax"] = Field(
        ..., description="평가 방법"
    )
    status: Literal["not_requested", "pending", "approved", "in_progress", "completed"] = Field(
        ..., description="평가 상태"
    )
    step: Optional[int] = Field(None, ge=1, le=14, description="단계 번호 (선택)")

class UpdateStatusResponse(BaseModel):
    """상태 업데이트 응답 모델"""
    status: str = Field(..., description="업데이트 상태")
    message: str = Field(..., description="응답 메시지")

# ============================================================
# Helper Functions
# ============================================================

async def validate_project_exists(project_id: str) -> dict:
    """프로젝트 존재 여부 확인"""
    try:
        projects = await supabase_client.select(
            "projects",
            filters={"id": project_id}
        )
        if not projects:
            raise HTTPException(
                status_code=404,
                detail=f"Project not found: {project_id}"
            )
        return projects[0]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating project: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to validate project: {str(e)}"
        )

def get_field_names(method: str) -> tuple[str, str]:
    """평가법에 따른 필드명 반환"""
    return f"{method}_status", f"{method}_step"

def calculate_progress(step: int) -> int:
    """단계 번호로부터 진행률 계산"""
    return int((step / MAX_STEP) * 100)

def get_status_message(status: str, step: int) -> str:
    """상태 메시지 생성"""
    messages = {
        "not_requested": "평가가 신청되지 않았습니다",
        "pending": "승인 대기 중입니다",
        "approved": "승인되었습니다",
        "in_progress": f"진행 중입니다 (단계 {step}/14)",
        "completed": "평가가 완료되었습니다"
    }
    return messages.get(status, "알 수 없는 상태")

# ============================================================
# API Endpoints
# ============================================================

@router.post("/start", response_model=StartValuationResponse)
async def start_valuation(request: StartValuationRequest):
    """
    평가 시작

    - 프로젝트의 특정 평가법을 시작합니다
    - status를 'in_progress'로, step을 5로 설정합니다
    """
    logger.info(f"Starting valuation: project_id={request.project_id}, method={request.method}")

    try:
        # 프로젝트 존재 확인
        await validate_project_exists(request.project_id)

        # 필드명 생성
        status_field, step_field = get_field_names(request.method)

        # 상태 업데이트
        update_data = {
            status_field: "in_progress",
            step_field: 5,
            "updated_at": datetime.utcnow().isoformat()
        }

        await supabase_client.update(
            "projects",
            update_data,
            filters={"id": request.project_id}
        )

        logger.info(f"Valuation started successfully: {request.project_id} - {request.method}")

        return StartValuationResponse(
            status="started",
            project_id=request.project_id,
            method=request.method,
            message=f"{request.method.upper()} 평가가 시작되었습니다 (단계 5/14)"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting valuation: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start valuation: {str(e)}"
        )

@router.get("/progress", response_model=ProgressResponse)
async def get_progress(
    project_id: str = Query(..., description="프로젝트 ID"),
    method: Literal["dcf", "relative", "intrinsic", "asset", "inheritance_tax"] = Query(
        ..., description="평가 방법"
    )
):
    """
    진행 상황 조회

    - 프로젝트의 특정 평가법 진행 상황을 조회합니다
    - 진행률, 현재 단계, 상태를 반환합니다
    """
    logger.info(f"Getting progress: project_id={project_id}, method={method}")

    try:
        # 프로젝트 조회
        project = await validate_project_exists(project_id)

        # 필드명 생성
        status_field, step_field = get_field_names(method)

        # 상태 및 단계 추출
        status = project.get(status_field, "not_requested")
        step = project.get(step_field, 1)

        # 진행률 계산
        progress = calculate_progress(step)

        # 메시지 생성
        message = get_status_message(status, step)

        return ProgressResponse(
            progress=progress,
            current_step=step,
            status=status,
            message=message
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting progress: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get progress: {str(e)}"
        )

@router.get("/result", response_model=ResultResponse)
async def get_result(
    project_id: str = Query(..., description="프로젝트 ID"),
    method: Literal["dcf", "relative", "intrinsic", "asset", "inheritance_tax"] = Query(
        ..., description="평가 방법"
    )
):
    """
    평가 결과 조회

    - 완료된 평가의 결과를 조회합니다
    - 평가 금액, 보고서 URL 등을 반환합니다
    """
    logger.info(f"Getting result: project_id={project_id}, method={method}")

    try:
        # 프로젝트 조회
        project = await validate_project_exists(project_id)

        # 필드명 생성
        status_field, _ = get_field_names(method)

        # 상태 확인
        status = project.get(status_field, "not_requested")
        if status != "completed":
            raise HTTPException(
                status_code=400,
                detail=f"Valuation is not completed yet. Current status: {status}"
            )

        # 결과 데이터 추출 (실제 구현에서는 별도 테이블에서 조회)
        # 현재는 더미 데이터 반환
        return ResultResponse(
            valuation_amount=None,  # TODO: 실제 평가 금액 조회
            currency="KRW",
            report_url=None,  # TODO: 실제 보고서 URL 조회
            completed_at=project.get("updated_at")
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting result: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get result: {str(e)}"
        )

@router.post("/advance-step", response_model=AdvanceStepResponse)
async def advance_step(request: AdvanceStepRequest):
    """
    다음 단계로 전진 (테스트용)

    - 현재 단계에서 다음 단계로 전진합니다
    - 단계 14에서는 더 이상 전진하지 않습니다
    """
    logger.info(f"Advancing step: project_id={request.project_id}, method={request.method}")

    try:
        # 프로젝트 조회
        project = await validate_project_exists(request.project_id)

        # 필드명 생성
        status_field, step_field = get_field_names(request.method)

        # 현재 단계 확인
        current_step = project.get(step_field, 1)

        if current_step >= MAX_STEP:
            raise HTTPException(
                status_code=400,
                detail=f"Already at maximum step: {MAX_STEP}"
            )

        # 다음 단계로 전진
        new_step = current_step + 1
        update_data = {
            step_field: new_step,
            "updated_at": datetime.utcnow().isoformat()
        }

        # 마지막 단계면 상태를 completed로 변경
        if new_step == MAX_STEP:
            update_data[status_field] = "completed"

        await supabase_client.update(
            "projects",
            update_data,
            filters={"id": request.project_id}
        )

        logger.info(f"Step advanced: {request.project_id} - {request.method} - step {new_step}")

        return AdvanceStepResponse(
            status="advanced",
            new_step=new_step,
            message=f"단계가 {current_step}에서 {new_step}(으)로 전진했습니다"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error advancing step: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to advance step: {str(e)}"
        )

@router.post("/update-status", response_model=UpdateStatusResponse)
async def update_status(request: UpdateStatusRequest):
    """
    평가 상태 업데이트

    - 프로젝트의 특정 평가법 상태를 업데이트합니다
    - 선택적으로 단계도 함께 업데이트할 수 있습니다
    """
    logger.info(
        f"Updating status: project_id={request.project_id}, "
        f"method={request.method}, status={request.status}, step={request.step}"
    )

    try:
        # 프로젝트 존재 확인
        await validate_project_exists(request.project_id)

        # 필드명 생성
        status_field, step_field = get_field_names(request.method)

        # 업데이트 데이터 준비
        update_data = {
            status_field: request.status,
            "updated_at": datetime.utcnow().isoformat()
        }

        # 단계가 제공되면 함께 업데이트
        if request.step is not None:
            update_data[step_field] = request.step

        await supabase_client.update(
            "projects",
            update_data,
            filters={"id": request.project_id}
        )

        logger.info(
            f"Status updated: {request.project_id} - {request.method} - {request.status}"
        )

        step_msg = f" (단계 {request.step})" if request.step else ""
        return UpdateStatusResponse(
            status="updated",
            message=f"상태가 '{request.status}'(으)로 업데이트되었습니다{step_msg}"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update status: {str(e)}"
        )
