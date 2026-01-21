"""
Authentication and Authorization

JWT 기반 인증 및 역할별 권한 관리
"""

from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv()

# 설정
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# 비밀번호 해싱
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Bearer 토큰
security = HTTPBearer()


# ========================================
# 역할 정의
# ========================================

class UserRole:
    """사용자 역할"""
    CUSTOMER = "customer"      # 고객
    ADMIN = "admin"           # 관리자
    ACCOUNTANT = "accountant" # 회계사
    SYSTEM = "system"         # 시스템 (내부 API)


# ========================================
# 토큰 페이로드 스키마
# ========================================

class TokenData(BaseModel):
    """JWT 토큰 페이로드"""
    user_id: str
    email: str
    role: str
    exp: Optional[datetime] = None


class User(BaseModel):
    """사용자 정보"""
    user_id: str
    email: str
    role: str
    name: Optional[str] = None


# ========================================
# 토큰 생성/검증
# ========================================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    JWT 액세스 토큰 생성

    Args:
        data: 토큰에 포함할 데이터 (user_id, email, role)
        expires_delta: 만료 시간 (기본: 30분)

    Returns:
        str: JWT 토큰
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> TokenData:
    """
    JWT 토큰 검증

    Args:
        token: JWT 토큰

    Returns:
        TokenData: 토큰 페이로드

    Raises:
        HTTPException: 토큰이 유효하지 않을 경우
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("user_id")
        email: str = payload.get("email")
        role: str = payload.get("role")

        if user_id is None or email is None or role is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="토큰 페이로드가 유효하지 않습니다.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return TokenData(user_id=user_id, email=email, role=role)

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="토큰이 유효하지 않습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ========================================
# 의존성 (Dependencies)
# ========================================

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """
    현재 로그인한 사용자 정보 가져오기

    Args:
        credentials: Bearer 토큰

    Returns:
        User: 사용자 정보

    Raises:
        HTTPException: 인증 실패 시
    """
    token = credentials.credentials
    token_data = verify_token(token)

    return User(
        user_id=token_data.user_id,
        email=token_data.email,
        role=token_data.role
    )


def require_role(*allowed_roles: str):
    """
    역할 기반 권한 체크 데코레이터

    Args:
        allowed_roles: 허용된 역할 목록

    Returns:
        Dependency: FastAPI 의존성

    Example:
        @router.post("/admin-only")
        async def admin_only_endpoint(user: User = Depends(require_role(UserRole.ADMIN))):
            ...
    """
    async def role_checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"권한이 없습니다. 필요한 역할: {', '.join(allowed_roles)}"
            )
        return user

    return role_checker


# 역할별 의존성 (편의 함수)
def get_customer_user(user: User = Depends(require_role(UserRole.CUSTOMER))) -> User:
    """고객 사용자만 허용"""
    return user


def get_admin_user(user: User = Depends(require_role(UserRole.ADMIN))) -> User:
    """관리자만 허용"""
    return user


def get_accountant_user(user: User = Depends(require_role(UserRole.ACCOUNTANT))) -> User:
    """회계사만 허용"""
    return user


def get_system_user(user: User = Depends(require_role(UserRole.SYSTEM))) -> User:
    """시스템 내부 API만 허용"""
    return user


# ========================================
# 비밀번호 해싱
# ========================================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """비밀번호 검증"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """비밀번호 해싱"""
    return pwd_context.hash(password)
