"""
Report Generator Service

기업 평가 보고서 PDF 생성 서비스
"""

from typing import Dict, Any, Optional
from datetime import datetime
import os
from supabase import create_client, Client
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()


class ReportGenerator:
    """
    평가 보고서 PDF 생성기

    Purpose: 평가 결과를 기반으로 전문적인 PDF 보고서 생성

    Report Structure (9 sections):
        1. 요약 (Executive Summary)
        2. 평가 개요 (Evaluation Overview)
        3. 회사 개요 및 산업 분석 (Company & Industry Analysis)
        4. 재무 분석 (Financial Analysis)
        5. 평가 방법론 및 가정 (Methodology & Assumptions)
        6. 평가 결과 (Valuation Results)
        7. 민감도 분석 (Sensitivity Analysis)
        8. 결론 (Conclusion)
        9. 부록 (Appendix)
    """

    def __init__(self, project_id: str, method: str):
        """
        초기화

        Args:
            project_id: 프로젝트 ID
            method: 평가법 ('dcf', 'relative', 'capital_market_law', 'asset', 'inheritance_tax_law', 'comprehensive')
        """
        self.project_id = project_id
        self.method = method

        # Supabase 클라이언트 초기화
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")

        if not supabase_url or not supabase_key:
            raise ValueError("Supabase URL과 KEY가 설정되지 않았습니다.")

        self.supabase: Client = create_client(supabase_url, supabase_key)

    async def generate_report(
        self,
        valuation_result: Dict[str, Any],
        mode: str = 'draft',
        options: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        PDF 보고서 생성

        Args:
            valuation_result: 평가 엔진 출력 결과
                {
                    'method_results': List[Dict],   # 개별 평가법 결과
                    'final_value': float,           # 최종 기업가치
                    'value_range': Dict,            # 평가 범위
                    'weighted_average': float,      # 가중평균 가치
                    'recommendation': str           # 최종 의견
                }
            mode: 'draft' (초안) 또는 'final' (최종본)
            options: 추가 옵션
                {
                    'include_appendix': bool,      # 부록 포함 여부 (default: True)
                    'watermark': bool,             # 워터마크 포함 (default: False)
                    'language': str                # 언어 ('ko', 'en')
                }

        Returns:
            str: Supabase Storage에 업로드된 PDF URL
        """
        # 기본 옵션 설정
        if options is None:
            options = {}

        include_appendix = options.get('include_appendix', True)
        watermark = options.get('watermark', False)
        language = options.get('language', 'ko')

        # 1. 프로젝트 데이터 로드
        project_data = await self._load_project_data()

        if not project_data:
            raise ValueError(f"프로젝트를 찾을 수 없습니다: {self.project_id}")

        # 2. 템플릿 선택
        template = self._get_template(language)

        # 3. 보고서 데이터 준비
        report_data = self._prepare_report_data(
            project_data,
            valuation_result,
            mode,
            include_appendix,
            watermark
        )

        # 4. HTML 렌더링
        html_content = self._render_html(template, report_data)

        # 5. PDF 변환
        pdf_bytes = await self._convert_to_pdf(html_content, watermark)

        # 6. Supabase Storage에 업로드
        filename = self._generate_filename(mode)
        pdf_url = await self._upload_to_storage(pdf_bytes, filename)

        # 7. 보고서 메타데이터 DB 저장
        await self._save_report_metadata(
            pdf_url,
            filename,
            mode,
            options
        )

        return pdf_url

    async def _load_project_data(self) -> Optional[Dict[str, Any]]:
        """
        프로젝트 정보 로드

        Returns:
            Dict: 프로젝트 데이터 또는 None
        """
        try:
            response = self.supabase.table('projects').select('*').eq('project_id', self.project_id).execute()

            if response.data and len(response.data) > 0:
                return response.data[0]

            return None
        except Exception as e:
            print(f"❌ 프로젝트 로드 실패: {e}")
            return None

    def _get_template(self, language: str = 'ko') -> str:
        """
        평가법별 HTML 템플릿 반환

        Args:
            language: 언어 ('ko' 또는 'en')

        Returns:
            str: HTML 템플릿
        """
        # 기본 템플릿 구조 (9개 섹션)
        if language == 'ko':
            template = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>기업가치평가 보고서</title>
    <style>
        @page {
            size: A4;
            margin: 2cm;
        }
        body {
            font-family: 'Noto Sans KR', sans-serif;
            line-height: 1.6;
            color: #333;
        }
        .cover-page {
            text-align: center;
            padding-top: 5cm;
        }
        .cover-page h1 {
            font-size: 32pt;
            margin-bottom: 2cm;
        }
        .section {
            page-break-before: always;
            margin-top: 1cm;
        }
        .section-title {
            font-size: 20pt;
            color: #1a237e;
            border-bottom: 2px solid #1a237e;
            padding-bottom: 0.5cm;
            margin-bottom: 1cm;
        }
        .table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 1cm;
        }
        .table th, .table td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        .table th {
            background-color: #f5f5f5;
            font-weight: bold;
        }
        .highlight {
            background-color: #fff9c4;
            padding: 10px;
            border-left: 4px solid #fbc02d;
            margin: 1cm 0;
        }
        .footer {
            position: fixed;
            bottom: 1cm;
            right: 1cm;
            font-size: 10pt;
            color: #999;
        }
    </style>
</head>
<body>
    <!-- Cover Page -->
    <div class="cover-page">
        <h1>기업가치평가 보고서</h1>
        <p style="font-size: 18pt;">{{ company_name }}</p>
        <p style="font-size: 14pt; margin-top: 2cm;">평가 기준일: {{ valuation_date }}</p>
        <p style="font-size: 12pt; margin-top: 1cm;">{{ report_mode }}</p>
    </div>

    <!-- Section 1: Executive Summary -->
    <div class="section">
        <h2 class="section-title">1. 요약 (Executive Summary)</h2>
        {{ executive_summary }}
    </div>

    <!-- Section 2: Evaluation Overview -->
    <div class="section">
        <h2 class="section-title">2. 평가 개요 (Evaluation Overview)</h2>
        {{ evaluation_overview }}
    </div>

    <!-- Section 3: Company & Industry Analysis -->
    <div class="section">
        <h2 class="section-title">3. 회사 개요 및 산업 분석</h2>
        {{ company_analysis }}
    </div>

    <!-- Section 4: Financial Analysis -->
    <div class="section">
        <h2 class="section-title">4. 재무 분석 (Financial Analysis)</h2>
        {{ financial_analysis }}
    </div>

    <!-- Section 5: Methodology & Assumptions -->
    <div class="section">
        <h2 class="section-title">5. 평가 방법론 및 가정</h2>
        {{ methodology }}
    </div>

    <!-- Section 6: Valuation Results -->
    <div class="section">
        <h2 class="section-title">6. 평가 결과 (Valuation Results)</h2>
        {{ valuation_results }}
    </div>

    <!-- Section 7: Sensitivity Analysis -->
    <div class="section">
        <h2 class="section-title">7. 민감도 분석 (Sensitivity Analysis)</h2>
        {{ sensitivity_analysis }}
    </div>

    <!-- Section 8: Conclusion -->
    <div class="section">
        <h2 class="section-title">8. 결론 (Conclusion)</h2>
        {{ conclusion }}
    </div>

    <!-- Section 9: Appendix (Optional) -->
    {% if include_appendix %}
    <div class="section">
        <h2 class="section-title">9. 부록 (Appendix)</h2>
        {{ appendix }}
    </div>
    {% endif %}

    <!-- Watermark (if enabled) -->
    {% if watermark %}
    <div style="position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%) rotate(-45deg);
                font-size: 72pt; color: rgba(200, 200, 200, 0.3); z-index: -1;">
        {{ watermark_text }}
    </div>
    {% endif %}

    <div class="footer">
        Generated on {{ generation_date }}
    </div>
</body>
</html>
            """
        else:
            # 영문 템플릿 (TODO: 추후 구현)
            template = "<!-- English template not yet implemented -->"

        return template

    def _prepare_report_data(
        self,
        project_data: Dict[str, Any],
        valuation_result: Dict[str, Any],
        mode: str,
        include_appendix: bool,
        watermark: bool
    ) -> Dict[str, Any]:
        """
        보고서 렌더링에 필요한 데이터 준비

        Returns:
            Dict: 템플릿 변수
        """
        return {
            # 기본 정보
            'company_name': project_data.get('company_name_kr', 'N/A'),
            'valuation_date': project_data.get('valuation_date', 'N/A'),
            'report_mode': '초안 (Draft)' if mode == 'draft' else '최종본 (Final)',
            'generation_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),

            # 섹션별 콘텐츠
            'executive_summary': self._generate_executive_summary(project_data, valuation_result),
            'evaluation_overview': self._generate_evaluation_overview(project_data),
            'company_analysis': self._generate_company_analysis(project_data),
            'financial_analysis': self._generate_financial_analysis(project_data),
            'methodology': self._generate_methodology(valuation_result),
            'valuation_results': self._generate_valuation_results(valuation_result),
            'sensitivity_analysis': self._generate_sensitivity_analysis(valuation_result),
            'conclusion': self._generate_conclusion(valuation_result),
            'appendix': self._generate_appendix(project_data) if include_appendix else '',

            # 옵션
            'include_appendix': include_appendix,
            'watermark': watermark,
            'watermark_text': 'DRAFT' if mode == 'draft' else ''
        }

    def _generate_executive_summary(self, project_data: Dict, valuation_result: Dict) -> str:
        """1. 요약 (Executive Summary)"""
        final_value = valuation_result.get('final_value', 0)
        value_range = valuation_result.get('value_range', {})

        return f"""
        <div class="highlight">
            <h3>평가 결과 요약</h3>
            <ul>
                <li><strong>평가 대상:</strong> {project_data.get('company_name_kr', 'N/A')}</li>
                <li><strong>평가 기준일:</strong> {project_data.get('valuation_date', 'N/A')}</li>
                <li><strong>최종 기업가치:</strong> {final_value:,.0f}원</li>
                <li><strong>평가 범위:</strong> {value_range.get('min', 0):,.0f}원 ~ {value_range.get('max', 0):,.0f}원</li>
            </ul>
        </div>
        <p>
            본 보고서는 {project_data.get('company_name_kr', 'N/A')}의 기업가치를 평가한 결과입니다.
            {len(valuation_result.get('method_results', []))}가지 평가법을 적용하여 종합적인 의견을 도출하였습니다.
        </p>
        """

    def _generate_evaluation_overview(self, project_data: Dict) -> str:
        """2. 평가 개요"""
        return f"""
        <h3>2.1 평가 목적</h3>
        <p>{project_data.get('valuation_purpose', 'N/A')}</p>

        <h3>2.2 평가 범위</h3>
        <p>평가 대상: {project_data.get('company_name_kr', 'N/A')}</p>
        <p>평가 기준일: {project_data.get('valuation_date', 'N/A')}</p>

        <h3>2.3 평가 방법</h3>
        <ul>
            {''.join([f'<li>{method}</li>' for method in project_data.get('valuation_methods', [])])}
        </ul>
        """

    def _generate_company_analysis(self, project_data: Dict) -> str:
        """3. 회사 개요 및 산업 분석"""
        return f"""
        <h3>3.1 회사 개요</h3>
        <table class="table">
            <tr><th>항목</th><th>내용</th></tr>
            <tr><td>회사명</td><td>{project_data.get('company_name_kr', 'N/A')}</td></tr>
            <tr><td>대표자</td><td>{project_data.get('ceo_name', 'N/A')}</td></tr>
            <tr><td>설립일</td><td>{project_data.get('founded_date', 'N/A')}</td></tr>
            <tr><td>업종</td><td>{project_data.get('industry', 'N/A')}</td></tr>
            <tr><td>상장 여부</td><td>{'상장' if project_data.get('is_listed') else '비상장'}</td></tr>
        </table>

        <h3>3.2 산업 분석</h3>
        <p>업종: {project_data.get('industry', 'N/A')}</p>
        <p>(산업 분석 내용은 추후 AI 엔진을 통해 자동 생성 예정)</p>
        """

    def _generate_financial_analysis(self, project_data: Dict) -> str:
        """4. 재무 분석"""
        return """
        <h3>4.1 재무 현황</h3>
        <p>(재무제표 데이터는 Document 업로드 후 파싱하여 자동 삽입 예정)</p>

        <h3>4.2 주요 재무 비율</h3>
        <p>(수익성, 안정성, 성장성 지표는 재무 데이터 기반으로 자동 계산 예정)</p>
        """

    def _generate_methodology(self, valuation_result: Dict) -> str:
        """5. 평가 방법론 및 가정"""
        method_results = valuation_result.get('method_results', [])

        method_descriptions = {
            'dcf': 'DCF(Discounted Cash Flow) 평가법: 미래 현금흐름의 현재가치를 계산',
            'relative': '상대가치평가법: 유사 기업의 배수(Multiple)를 적용',
            'capital_market_law': '본질가치평가법: 자본시장법상 기업인수목적회사(SPAC) 평가',
            'asset': '자산가치평가법: 순자산가치(NAV) 기준 평가',
            'inheritance_tax_law': '상증세법평가법: 상속세 및 증여세법상 평가'
        }

        methods_html = ""
        for i, method_result in enumerate(method_results, 1):
            method = method_result.get('method', '')
            method_name = method_result.get('method_name', '')
            description = method_descriptions.get(method, '')

            methods_html += f"""
            <h3>5.{i} {method_name}</h3>
            <p>{description}</p>
            <p><strong>적용 가중치:</strong> {method_result.get('weight', 0):.1%}</p>
            """

        return methods_html

    def _generate_valuation_results(self, valuation_result: Dict) -> str:
        """6. 평가 결과"""
        method_results = valuation_result.get('method_results', [])

        # 평가법별 결과 테이블
        table_rows = ""
        for method_result in method_results:
            method_name = method_result.get('method_name', 'N/A')
            equity_value = method_result.get('equity_value', 0)
            weight = method_result.get('weight', 0)
            status = '✅' if method_result.get('success') else '❌'

            table_rows += f"""
            <tr>
                <td>{status} {method_name}</td>
                <td style="text-align: right;">{equity_value:,.0f}원</td>
                <td style="text-align: right;">{weight:.1%}</td>
            </tr>
            """

        final_value = valuation_result.get('final_value', 0)

        return f"""
        <h3>6.1 평가법별 결과</h3>
        <table class="table">
            <tr>
                <th>평가법</th>
                <th style="text-align: right;">기업가치</th>
                <th style="text-align: right;">가중치</th>
            </tr>
            {table_rows}
            <tr style="background-color: #e3f2fd; font-weight: bold;">
                <td>최종 기업가치</td>
                <td style="text-align: right;">{final_value:,.0f}원</td>
                <td style="text-align: right;">-</td>
            </tr>
        </table>

        <h3>6.2 평가 의견</h3>
        <div class="highlight">
            {valuation_result.get('recommendation', '')}
        </div>
        """

    def _generate_sensitivity_analysis(self, valuation_result: Dict) -> str:
        """7. 민감도 분석"""
        return """
        <h3>7.1 주요 가정 변동에 따른 기업가치 변화</h3>
        <p>(민감도 분석 테이블은 평가 엔진에서 계산된 데이터 기반으로 자동 생성 예정)</p>

        <h3>7.2 시나리오 분석</h3>
        <ul>
            <li><strong>낙관적 시나리오:</strong> (상위 10%)</li>
            <li><strong>기본 시나리오:</strong> (중간값)</li>
            <li><strong>비관적 시나리오:</strong> (하위 10%)</li>
        </ul>
        """

    def _generate_conclusion(self, valuation_result: Dict) -> str:
        """8. 결론"""
        final_value = valuation_result.get('final_value', 0)
        value_range = valuation_result.get('value_range', {})

        return f"""
        <h3>8.1 평가 결과 요약</h3>
        <p>본 평가 결과, 대상 기업의 기업가치는 <strong>{final_value:,.0f}원</strong>으로 평가됩니다.</p>
        <p>평가 범위: {value_range.get('min', 0):,.0f}원 ~ {value_range.get('max', 0):,.0f}원</p>

        <h3>8.2 평가 의견</h3>
        <p>{valuation_result.get('recommendation', '')}</p>

        <h3>8.3 유의사항</h3>
        <ul>
            <li>본 평가는 특정 시점({valuation_result.get('valuation_date', 'N/A')})을 기준으로 작성되었습니다.</li>
            <li>향후 경영 환경, 시장 상황 등의 변화에 따라 실제 가치는 달라질 수 있습니다.</li>
            <li>본 보고서는 평가 목적 외의 용도로 사용할 수 없습니다.</li>
        </ul>
        """

    def _generate_appendix(self, project_data: Dict) -> str:
        """9. 부록"""
        return """
        <h3>9.1 재무제표</h3>
        <p>(업로드된 재무제표 원본 데이터 첨부 예정)</p>

        <h3>9.2 평가법 상세 설명</h3>
        <p>(5가지 평가법의 이론적 배경 및 수식 설명 예정)</p>

        <h3>9.3 참고 자료</h3>
        <ul>
            <li>자본시장법</li>
            <li>상속세 및 증여세법</li>
            <li>한국공인회계사회 평가 실무 지침</li>
        </ul>
        """

    def _render_html(self, template: str, data: Dict[str, Any]) -> str:
        """
        Jinja2를 사용하여 HTML 렌더링

        Args:
            template: HTML 템플릿
            data: 템플릿 변수

        Returns:
            str: 렌더링된 HTML
        """
        # 현재는 간단한 문자열 치환 사용
        # 실제 구현 시 Jinja2 사용 권장
        html = template
        for key, value in data.items():
            placeholder = "{{ " + key + " }}"
            html = html.replace(placeholder, str(value))

        return html

    async def _convert_to_pdf(self, html: str, watermark: bool = False) -> bytes:
        """
        HTML을 PDF로 변환

        Args:
            html: HTML 문자열
            watermark: 워터마크 포함 여부

        Returns:
            bytes: PDF 바이트
        """
        try:
            from weasyprint import HTML, CSS
            from io import BytesIO

            # Watermark CSS
            watermark_css = """
            @page {
                @bottom-center {
                    content: "DRAFT - 초안";
                    font-size: 60px;
                    color: rgba(200, 200, 200, 0.3);
                    font-weight: bold;
                }
            }
            """ if watermark else ""

            # HTML to PDF conversion
            pdf_file = BytesIO()
            HTML(string=html).write_pdf(
                pdf_file,
                stylesheets=[CSS(string=watermark_css)] if watermark else None
            )

            return pdf_file.getvalue()

        except ImportError:
            # weasyprint가 없으면 mock PDF 반환
            print("⚠️ weasyprint not installed. Returning mock PDF.")
            mock_pdf_content = f"""
            Mock PDF Report
            =================
            Generated at: {datetime.now()}
            Watermark: {watermark}

            HTML Preview:
            {html[:500]}...
            """
            return mock_pdf_content.encode('utf-8')
        except Exception as e:
            print(f"❌ PDF 변환 실패: {e}")
            raise

    async def _upload_to_storage(self, pdf_bytes: bytes, filename: str) -> str:
        """
        Supabase Storage에 PDF 업로드

        Args:
            pdf_bytes: PDF 바이트
            filename: 파일명

        Returns:
            str: Public URL
        """
        try:
            # Supabase Storage 버킷 이름
            bucket_name = 'reports'

            # 파일 경로
            file_path = f"{self.project_id}/{filename}"

            # 업로드
            self.supabase.storage.from_(bucket_name).upload(
                file_path,
                pdf_bytes,
                file_options={"content-type": "application/pdf"}
            )

            # Public URL 생성
            public_url = self.supabase.storage.from_(bucket_name).get_public_url(file_path)

            return public_url

        except Exception as e:
            print(f"❌ Storage 업로드 실패: {e}")
            # Mock URL 반환 (개발용)
            return f"https://mock-storage.supabase.co/reports/{self.project_id}/{filename}"

    async def _save_report_metadata(
        self,
        pdf_url: str,
        filename: str,
        mode: str,
        options: Dict[str, Any]
    ):
        """
        보고서 메타데이터를 DB에 저장

        Args:
            pdf_url: PDF URL
            filename: 파일명
            mode: 'draft' 또는 'final'
            options: 추가 옵션
        """
        try:
            report_id = f"RPT-{self.project_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"

            report_data = {
                'report_id': report_id,
                'project_id': self.project_id,
                'report_type': 'comprehensive' if self.method == 'comprehensive' else 'single_method',
                'delivery_format': 'pdf',
                'delivery_method': 'download',
                'include_appendix': options.get('include_appendix', True),
                'watermark': options.get('watermark', False),
                'report_url': pdf_url,
                'report_path': f"{self.project_id}/{filename}",
                'issued_at': datetime.now().isoformat(),
                'issued_by': None  # TODO: 현재 로그인 사용자 정보
            }

            self.supabase.table('reports').insert(report_data).execute()

            print(f"✅ 보고서 메타데이터 저장 완료: {report_id}")

        except Exception as e:
            print(f"❌ 메타데이터 저장 실패: {e}")

    def _generate_filename(self, mode: str) -> str:
        """
        파일명 생성

        Args:
            mode: 'draft' 또는 'final'

        Returns:
            str: 파일명
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        mode_suffix = 'DRAFT' if mode == 'draft' else 'FINAL'

        return f"Valuation_Report_{self.project_id}_{mode_suffix}_{timestamp}.pdf"


# 사용 예시
if __name__ == "__main__":
    import asyncio

    async def test_report_generator():
        """테스트 함수"""

        # 테스트 데이터
        project_id = "SAMSU-2501191430-CP"
        method = "comprehensive"

        valuation_result = {
            'method_results': [
                {
                    'method': 'dcf',
                    'method_name': 'DCF평가법',
                    'equity_value': 1000000000,
                    'weight': 0.4,
                    'success': True,
                    'note': ''
                },
                {
                    'method': 'relative',
                    'method_name': '상대가치평가법',
                    'equity_value': 950000000,
                    'weight': 0.3,
                    'success': True,
                    'note': ''
                }
            ],
            'final_value': 980000000,
            'value_range': {
                'min': 950000000,
                'median': 975000000,
                'max': 1000000000
            },
            'weighted_average': 980000000,
            'recommendation': '본 기업은 안정적인 수익 구조를 가지고 있으며, 종합 평가 결과 약 9억 8천만원의 기업가치를 가진 것으로 판단됩니다.'
        }

        # 보고서 생성
        generator = ReportGenerator(project_id, method)

        try:
            pdf_url = await generator.generate_report(
                valuation_result,
                mode='draft',
                options={
                    'include_appendix': True,
                    'watermark': True,
                    'language': 'ko'
                }
            )

            print(f"✅ 보고서 생성 완료!")
            print(f"📄 PDF URL: {pdf_url}")

        except Exception as e:
            print(f"❌ 보고서 생성 실패: {e}")

    # 비동기 실행
    asyncio.run(test_report_generator())
