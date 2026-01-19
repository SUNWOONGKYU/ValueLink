"""
Supabase Client
Supabase REST API 클라이언트

@task Investment Tracker
@description Supabase DB와 통신하는 클라이언트
"""
import httpx
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from app.core.config import settings


class SupabaseClient:
    """
    Supabase REST API 클라이언트
    PostgREST API를 사용하여 데이터베이스와 통신
    """

    def __init__(self):
        self.url = settings.SUPABASE_URL
        self.key = settings.SUPABASE_KEY
        self.headers = {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }

    async def _request(
        self,
        method: str,
        table: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        filters: Optional[str] = ""
    ) -> Any:
        """HTTP 요청 실행"""
        url = f"{self.url}/rest/v1/{table}{filters}"

        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=method,
                url=url,
                headers=self.headers,
                params=params,
                json=data
            )
            response.raise_for_status()

            if response.content:
                return response.json()
            return None

    # ============================================================
    # Generic CRUD Operations
    # ============================================================

    async def select(
        self,
        table: str,
        columns: str = "*",
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Dict]:
        """SELECT 쿼리"""
        params = {"select": columns}

        # 필터 적용
        if filters:
            for key, value in filters.items():
                if value is not None:
                    params[key] = f"eq.{value}"

        if order_by:
            params["order"] = order_by
        if limit:
            params["limit"] = limit
        if offset:
            params["offset"] = offset

        return await self._request("GET", table, params=params)

    async def insert(self, table: str, data: Dict) -> Dict:
        """INSERT 쿼리"""
        result = await self._request("POST", table, data=data)
        return result[0] if result else {}

    async def update(
        self,
        table: str,
        data: Dict,
        filters: Dict[str, Any]
    ) -> List[Dict]:
        """UPDATE 쿼리"""
        filter_str = "?" + "&".join([f"{k}=eq.{v}" for k, v in filters.items()])
        return await self._request("PATCH", table, data=data, filters=filter_str)

    async def delete(self, table: str, filters: Dict[str, Any]) -> None:
        """DELETE 쿼리"""
        filter_str = "?" + "&".join([f"{k}=eq.{v}" for k, v in filters.items()])
        await self._request("DELETE", table, filters=filter_str)

    async def count(self, table: str, filters: Optional[Dict[str, Any]] = None) -> int:
        """COUNT 쿼리"""
        headers = {**self.headers, "Prefer": "count=exact"}
        params = {"select": "*"}

        if filters:
            for key, value in filters.items():
                if value is not None:
                    params[key] = f"eq.{value}"

        url = f"{self.url}/rest/v1/{table}"

        async with httpx.AsyncClient() as client:
            response = await client.head(url, headers=headers, params=params)
            content_range = response.headers.get("content-range", "0-0/0")
            total = int(content_range.split("/")[-1])
            return total

    # ============================================================
    # Investment Tracker Specific Methods
    # ============================================================

    async def get_companies(
        self,
        page: int = 1,
        page_size: int = 20,
        industry: Optional[str] = None,
        stage: Optional[str] = None,
        search: Optional[str] = None
    ) -> Dict:
        """기업 목록 조회"""
        params = {
            "select": "*",
            "order": "latest_round_date.desc.nullslast",
            "limit": page_size,
            "offset": (page - 1) * page_size
        }

        if industry:
            params["industry"] = f"eq.{industry}"
        if stage:
            params["latest_stage"] = f"eq.{stage}"
        if search:
            params["name_ko"] = f"ilike.%{search}%"

        items = await self._request("GET", "startup_companies", params=params)
        total = await self.count("startup_companies")

        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }

    async def get_company_by_id(self, company_id: int) -> Optional[Dict]:
        """기업 상세 조회"""
        result = await self.select(
            "startup_companies",
            filters={"id": company_id}
        )
        return result[0] if result else None

    async def get_company_by_name(self, name_ko: str) -> Optional[Dict]:
        """기업명으로 조회"""
        result = await self.select(
            "startup_companies",
            filters={"name_ko": name_ko}
        )
        return result[0] if result else None

    async def create_company(self, data: Dict) -> Dict:
        """기업 생성"""
        data["created_at"] = datetime.utcnow().isoformat()
        data["updated_at"] = datetime.utcnow().isoformat()
        data["first_discovered_at"] = datetime.utcnow().isoformat()
        return await self.insert("startup_companies", data)

    async def update_company(self, company_id: int, data: Dict) -> Dict:
        """기업 수정"""
        data["updated_at"] = datetime.utcnow().isoformat()
        result = await self.update(
            "startup_companies",
            data,
            filters={"id": company_id}
        )
        return result[0] if result else {}

    async def get_investment_rounds(self, company_id: int) -> List[Dict]:
        """투자 라운드 조회"""
        return await self.select(
            "investment_rounds",
            filters={"company_id": company_id},
            order_by="round_date.desc"
        )

    async def create_investment_round(self, data: Dict) -> Dict:
        """투자 라운드 생성"""
        data["created_at"] = datetime.utcnow().isoformat()
        data["updated_at"] = datetime.utcnow().isoformat()
        return await self.insert("investment_rounds", data)

    async def get_news(
        self,
        page: int = 1,
        page_size: int = 20,
        source: Optional[str] = None,
        company_id: Optional[int] = None
    ) -> Dict:
        """뉴스 목록 조회"""
        params = {
            "select": "*",
            "order": "published_date.desc.nullslast",
            "limit": page_size,
            "offset": (page - 1) * page_size
        }

        if source:
            params["source"] = f"eq.{source}"
        if company_id:
            params["company_id"] = f"eq.{company_id}"

        items = await self._request("GET", "investment_news", params=params)
        total = await self.count("investment_news")

        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }

    async def get_news_by_url(self, source_url: str) -> Optional[Dict]:
        """URL로 뉴스 조회"""
        result = await self.select(
            "investment_news",
            filters={"source_url": source_url}
        )
        return result[0] if result else None

    async def create_news(self, data: Dict) -> Dict:
        """뉴스 생성"""
        data["created_at"] = datetime.utcnow().isoformat()
        data["updated_at"] = datetime.utcnow().isoformat()
        return await self.insert("investment_news", data)

    async def get_email_template(self, company_id: int) -> Optional[Dict]:
        """이메일 템플릿 조회"""
        params = {
            "select": "*",
            "company_id": f"eq.{company_id}",
            "is_active": "eq.true",
            "order": "version.desc",
            "limit": 1
        }
        result = await self._request("GET", "email_templates", params=params)
        return result[0] if result else None

    async def create_email_template(self, data: Dict) -> Dict:
        """이메일 템플릿 생성"""
        data["created_at"] = datetime.utcnow().isoformat()
        data["updated_at"] = datetime.utcnow().isoformat()
        return await self.insert("email_templates", data)

    async def get_collections(self, page: int = 1, page_size: int = 10) -> Dict:
        """수집 이력 조회"""
        params = {
            "select": "*",
            "order": "collection_date.desc",
            "limit": page_size,
            "offset": (page - 1) * page_size
        }
        items = await self._request("GET", "weekly_collections", params=params)
        total = await self.count("weekly_collections")

        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }

    async def create_collection(self, data: Dict) -> Dict:
        """수집 레코드 생성"""
        data["created_at"] = datetime.utcnow().isoformat()
        data["updated_at"] = datetime.utcnow().isoformat()
        return await self.insert("weekly_collections", data)

    async def update_collection(self, collection_id: int, data: Dict) -> Dict:
        """수집 레코드 수정"""
        data["updated_at"] = datetime.utcnow().isoformat()
        result = await self.update(
            "weekly_collections",
            data,
            filters={"id": collection_id}
        )
        return result[0] if result else {}

    async def get_dashboard_stats(self) -> Dict:
        """대시보드 통계"""
        from datetime import timedelta

        week_ago = (datetime.utcnow() - timedelta(days=7)).isoformat()

        # 기본 통계
        total_companies = await self.count("startup_companies")
        total_news = await self.count("investment_news")

        # 총 투자금액 (별도 쿼리 필요 - RPC 사용 권장)
        companies = await self.select("startup_companies", columns="total_funding_krw")
        total_funding = sum(c.get("total_funding_krw", 0) or 0 for c in companies)

        # 최근 수집
        collections = await self.select(
            "weekly_collections",
            order_by="collection_date.desc",
            limit=1
        )
        last_collection = collections[0] if collections else None

        return {
            "total_companies": total_companies,
            "total_news": total_news,
            "total_funding_krw": total_funding,
            "this_week_new_companies": 0,  # 별도 쿼리 필요
            "this_week_new_news": 0,       # 별도 쿼리 필요
            "industry_distribution": {},    # 별도 쿼리 필요
            "stage_distribution": {},       # 별도 쿼리 필요
            "last_collection_date": last_collection.get("collection_date") if last_collection else None,
            "last_collection_status": last_collection.get("status") if last_collection else None
        }


# 전역 인스턴스
supabase_client = SupabaseClient()
