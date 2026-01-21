"""
Database Configuration

PostgreSQL 데이터베이스 설정
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from typing import Generator
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# 데이터베이스 URL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://user:password@localhost:5432/valuation_db"
)

# SQLAlchemy Engine 생성
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # 연결 유효성 검사
    echo=False,  # SQL 로그 (개발 시 True)
)

# SessionLocal 클래스 생성
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# 데이터베이스 세션 의존성
def get_db() -> Generator[Session, None, None]:
    """
    FastAPI 의존성으로 사용할 데이터베이스 세션 생성

    Usage:
        @app.get("/items")
        def read_items(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 테이블 생성 함수
def create_tables():
    """
    모든 테이블 생성

    주의: Alembic을 사용하는 경우 이 함수 대신 마이그레이션 사용
    """
    from models import Base
    Base.metadata.create_all(bind=engine)
    print("✅ 모든 테이블이 생성되었습니다.")


# 테이블 삭제 함수 (개발용)
def drop_tables():
    """
    모든 테이블 삭제

    ⚠️ 주의: 프로덕션 환경에서 사용 금지!
    """
    from models import Base
    Base.metadata.drop_all(bind=engine)
    print("⚠️ 모든 테이블이 삭제되었습니다.")


if __name__ == "__main__":
    # 직접 실행 시 테이블 생성
    print("데이터베이스 테이블 생성 중...")
    create_tables()
