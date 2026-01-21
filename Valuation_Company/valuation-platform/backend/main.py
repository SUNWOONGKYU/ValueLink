"""
FastAPI Main Application

기업가치평가 플랫폼 백엔드 서버
- 5가지 평가법 지원: 1.DCF평가법 2.상대가치평가법 3.본질가치평가법 4.자산가치평가법 5.상증세법평가법
- 22개 인간 판단 포인트 관리
- 11단계 워크플로우 (requested → completed)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# 역할별 라우터 임포트
from routers import (
    customer_router,
    admin_router,
    accountant_router,
    internal_router
)

# 기존 라우터 (레퍼런스용 - 사용 안 함)
# from routers import (
#     projects,
#     documents,
#     ai_extraction,
#     calculations,
#     approvals,
#     drafts,
#     revisions,
#     reports,
#     master_valuation
# )

# FastAPI 앱 생성
app = FastAPI(
    title="기업가치평가 플랫폼 API",
    description="""
5가지 평가법을 지원하는 통합 기업가치평가 시스템

## 역할별 API 경로
- **고객**: `/api/customer/*` - 평가 신청, 문서 업로드, 수정 요청, 보고서 다운로드
- **관리자**: `/api/admin/*` - 견적서 발송, 협의, 승인, 프로젝트 조회
- **회계사**: `/api/accountant/*` - 판단 포인트 검토/승인, 초안 생성, 최종 확정, 보고서 발행
- **시스템/AI**: `/api/internal/*` - 데이터 추출, 평가 계산, 통합 평가

## 5가지 평가법 (순서 고정)
1. DCF평가법 (dcf)
2. 상대가치평가법 (relative)
3. 본질가치평가법 (capital_market_law)
4. 자산가치평가법 (asset)
5. 상증세법평가법 (inheritance_tax_law)

## 인증 방식
- JWT Bearer Token 사용
- 역할별 권한 관리 (customer, admin, accountant, system)
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 설정
origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 역할별 라우터 등록
app.include_router(customer_router.router, prefix="/api")
app.include_router(admin_router.router, prefix="/api")
app.include_router(accountant_router.router, prefix="/api")
app.include_router(internal_router.router, prefix="/api")

# 기존 라우터 등록 (주석 처리 - 역할별 라우터로 대체됨)
# app.include_router(projects.router, prefix="/api", tags=["Projects"])
# app.include_router(documents.router, prefix="/api", tags=["Documents"])
# app.include_router(ai_extraction.router, prefix="/api", tags=["AI Extraction"])
# app.include_router(calculations.router, prefix="/api", tags=["Calculations"])
# app.include_router(approvals.router, prefix="/api", tags=["Approval Points"])
# app.include_router(drafts.router, prefix="/api", tags=["Drafts"])
# app.include_router(revisions.router, prefix="/api", tags=["Revisions"])
# app.include_router(reports.router, prefix="/api", tags=["Reports"])
# app.include_router(master_valuation.router, prefix="/api", tags=["Master Valuation"])

# 헬스 체크
@app.get("/")
async def root():
    """
    API 서버 상태 확인
    """
    return {
        "status": "ok",
        "message": "기업가치평가 플랫폼 API 서버",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """
    서버 헬스 체크
    """
    return {
        "status": "healthy",
        "database": "connected"  # TODO: 실제 DB 연결 확인
    }

# 에러 핸들러
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    전역 에러 핸들러
    """
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_server_error",
            "message": str(exc),
            "detail": "서버 내부 오류가 발생했습니다."
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
