# 기업가치평가 플랫폼 MVP - Claude Code 작업지시서 (최종판)
## valuation.ai.kr

---

## 🎯 프로젝트 개요

### 핵심 목표
**첫 번째 고객 확보!** 이것이 MVP의 유일한 목표입니다.

### 사업 전략
```
1인 개발 → MVP 출시 → 첫 고객 확보 → 수익 발생 → 확장
```

### 차별화 포인트
1. **AI 자동화**: 5-7일 내 평가 완료 (기존: 2-3주)
2. **가격 경쟁력**: 기존 시장 대비 **50% 수준**
3. **이중 산출물 제공**:
   - PDF 평가보고서 (도장 찍힌 정식 문서)
   - 엑셀 계산 파일 (고객이 직접 수치 변경하여 재계산 가능)
4. **투명성**: 모든 계산 과정 공개
5. **무료 시뮬레이터**: 평가 신청 전 간단 테스트 제공

---

## 📊 개발 우선순위

### Phase 1: MVP (우선 개발) - 4주

**A. 정식 평가 서비스 (유료)**
```
1. DCF 평가 시스템
   - 평가 로직 (Python)
   - PDF 보고서 생성
   - 엑셀 계산 파일 생성 (고객이 수정 가능)
   
2. 상대가치 평가 시스템
   - 평가 로직
   - PDF 보고서 생성
   - 엑셀 계산 파일 생성
```

**B. 무료 체험 기능 (리드 생성)**
```
3. 웹 시뮬레이터 (3종)
   - DCF 간이 계산기 (React)
   - 상대가치 간이 계산기 (React)
   - 상증법 간이 계산기 (React)
   → 목적: 평가 신청 전 간단 테스트
   → [정식 평가 신청하기] 버튼으로 전환 유도
```

**C. 기본 웹사이트**
```
4. 메인 랜딩 페이지
   - 5가지 평가방법 소개
   - YouTube 콘텐츠 임베딩
   - 평가 신청 폼
```

### Phase 2: 확장 (MVP 이후) - +4주
```
1. IPO 평가
2. 상증법 평가
3. 자산가치평가
4. 랭킹 시스템
5. AI 아바타 IR
```

---

## 🔧 기술 스택

### Backend
```yaml
언어: Python 3.11+
프레임워크: FastAPI
데이터베이스: Supabase (PostgreSQL)
ORM: SQLAlchemy
AI: Claude API (Anthropic)
```

### Frontend
```yaml
프레임워크: Next.js 14 (App Router)
스타일링: Tailwind CSS
UI 라이브러리: shadcn/ui
차트: Recharts
```

### Deployment
```yaml
호스팅: Vercel
데이터베이스: Supabase (Managed PostgreSQL)
파일 저장: Supabase Storage
도메인: valuation.ai.kr (이미 확보됨)
```

### 개발 환경
```yaml
에디터: Cursor / VS Code
패키지 관리: npm / pip
버전 관리: Git
```

---

## 📁 프로젝트 구조

```
valuation-platform/
├── frontend/                 # Next.js 프론트엔드
│   ├── app/
│   │   ├── page.tsx         # 메인 페이지
│   │   ├── dcf/            # DCF 평가 신청
│   │   ├── comparable/      # 상대가치 평가
│   │   ├── simulator/       # 시뮬레이터
│   │   └── api/            # API 라우트
│   ├── components/          # 재사용 컴포넌트
│   ├── lib/                # 유틸리티
│   └── public/             # 정적 파일
│
├── backend/                 # FastAPI 백엔드
│   ├── app/
│   │   ├── main.py         # FastAPI 앱
│   │   ├── models/         # 데이터 모델
│   │   ├── routers/        # API 라우터
│   │   ├── services/       # 비즈니스 로직
│   │   │   ├── dcf_evaluator.py
│   │   │   ├── comparable_evaluator.py
│   │   │   ├── excel_generator.py
│   │   │   └── pdf_generator.py
│   │   └── utils/          # 유틸리티
│   └── tests/              # 테스트
│
├── docs/
    └── api-docs.md         # API 문서
```

---

## 💾 데이터베이스 스키마 (SQLAlchemy)

데이터베이스 스키마는 `backend/app/models/` 디렉토리 내의 Python 클래스들을 통해 SQLAlchemy 모델로 정의됩니다. Prisma 스키마 파일은 사용하지 않습니다.

주요 모델:
- `Company`
- `Evaluation`
- `User`

(자세한 필드는 `backend/app/models/` 내부 파일 참조)

---

## 📋 API 엔드포인트 설계

### DCF 평가 API
```python
# POST /api/v1/dcf/evaluate
# 요청
{
  "company_id": "uuid",
  "financial_data": {
    "revenue_history": [100, 120, 150],  # 최근 3년 매출
    "ebit_margin": 0.15,
    "tax_rate": 0.22,
    "growth_rate": 0.20,  # 향후 5년 성장률
    "terminal_growth": 0.03,
    "wacc": 0.10
  }
}

# 응답
{
  "evaluation_id": "uuid",
  "enterprise_value": 5000000000,
  "equity_value": 4500000000,
  "share_price": 45000,
  "excel_url": "https://...",
  "pdf_url": "https://..."
}
```

### 상대가치 평가 API
```python
# POST /api/v1/comparable/evaluate
# 요청
{
  "company_id": "uuid",
  "comparable_companies": ["A", "B", "C"],
  "metrics": {
    "revenue": 150000000,
    "ebitda": 30000000,
    "net_income": 20000000,
    "total_assets": 200000000
  }
}

# 응답
{
  "evaluation_id": "uuid",
  "per_value": 3000000000,
  "pbr_value": 2800000000,
  "ebitda_value": 3200000000,
  "average_value": 3000000000,
  "excel_url": "https://...",
  "pdf_url": "https://..."
}
```

---

## 🎨 주요 화면 설계

### 1. 메인 페이지 (/)
```
┌─────────────────────────────────────┐
│  Hero Section                        │
│  "AI가 5일만에 완성하는 기업가치평가" │
│  [DCF 평가 시작] [상대가치 평가]      │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│  5가지 평가 방법론 소개               │
│  ┌─────┐ ┌─────┐ ┌─────┐           │
│  │ DCF  │ │ 상대 │ │ IPO  │          │
│  └─────┘ └─────┘ └─────┘           │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│  무료 시뮬레이터 체험                 │
│  [DCF 계산기] [상대가치 계산기]       │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│  YouTube 콘텐츠 (50편 시리즈)        │
│  [EP 01] [EP 02] [EP 03] ...        │
└─────────────────────────────────────┘
```

### 2. DCF 평가 신청 (/dcf)
```
┌─────────────────────────────────────┐
│  Step 1: 기업 정보 입력               │
│  - 기업명, 사업자번호, 업종           │
│  - 대표자명, 설립일                   │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│  Step 2: 재무 데이터 입력             │
│  - 최근 3년 재무제표                  │
│  - 매출, 영업이익, 순이익             │
│  - 총자산, 부채, 자본                 │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│  Step 3: 사업계획 입력                │
│  - 향후 5년 성장률 전망               │
│  - 투자 계획                          │
│  - 주요 가정사항                      │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│  Step 4: 제출 및 결제                 │
│  - 평가 비용: (시장 조사 후 결정)     │
│  - 예상 완료일: 5-7일                 │
│  [제출하기]                           │
└─────────────────────────────────────┘
```

### 3. 시뮬레이터 (/simulator)
```
┌─────────────────────────────────────┐
│  DCF 간이 계산기                     │
│                                      │
│  입력:                                │
│  • 현재 연매출: [____] 억원           │
│  • 연평균 성장률: [__]%               │
│  • 할인율(WACC): [__]%                │
│  • 영구 성장률: [__]%                 │
│                                      │
│  [계산하기]                           │
│                                      │
│  결과:                                │
│  기업가치: 약 ____ 억원               │
│                                      │
│  ⚠️ 이것은 간이 계산입니다.           │
│  정확한 평가는 전문 서비스를 이용하세요│
│                                      │
│  [정식 평가 신청하기]                 │
└─────────────────────────────────────┘
```

---

## 🔨 1. DCF 평가 시스템 구현 가이드

### 1.1 DCF 평가 로직 (Python)

```python
# backend/app/services/dcf_evaluator.py

from typing import List, Dict
import numpy as np

class DCFEvaluator:
    """DCF 평가 엔진"""
    
    def __init__(self, financial_data: Dict):
        self.revenue_history = financial_data['revenue_history']
        self.ebit_margin = financial_data['ebit_margin']
        self.tax_rate = financial_data['tax_rate']
        self.growth_rate = financial_data['growth_rate']
        self.terminal_growth = financial_data['terminal_growth']
        self.wacc = financial_data['wacc']
        
    def calculate_fcf_projections(self, years: int = 5) -> List[float]:
        """5년간 FCF 예측"""
        fcf_list = []
        last_revenue = self.revenue_history[-1]
        
        for year in range(1, years + 1):
            revenue = last_revenue * ((1 + self.growth_rate) ** year)
            ebit = revenue * self.ebit_margin
            nopat = ebit * (1 - self.tax_rate)
            
            # 간소화: FCF ≈ NOPAT (운전자본/CAPEX 변화 무시)
            fcf = nopat * 0.85  # 보수적 조정
            fcf_list.append(fcf)
            
        return fcf_list
    
    def calculate_terminal_value(self, final_fcf: float) -> float:
        """영구가치 계산 (Gordon Growth Model)"""
        terminal_fcf = final_fcf * (1 + self.terminal_growth)
        terminal_value = terminal_fcf / (self.wacc - self.terminal_growth)
        return terminal_value
    
    def calculate_enterprise_value(self) -> Dict:
        """기업가치 계산"""
        # 1. 명시적 예측기간 FCF
        fcf_projections = self.calculate_fcf_projections()
        
        # 2. FCF 현재가치화
        pv_fcfs = []
        for year, fcf in enumerate(fcf_projections, start=1):
            pv = fcf / ((1 + self.wacc) ** year)
            pv_fcfs.append(pv)
        
        # 3. 터미널 가치
        terminal_value = self.calculate_terminal_value(fcf_projections[-1])
        pv_terminal = terminal_value / ((1 + self.wacc) ** len(fcf_projections))
        
        # 4. 기업가치
        enterprise_value = sum(pv_fcfs) + pv_terminal
        
        return {
            'enterprise_value': enterprise_value,
            'pv_fcfs': pv_fcfs,
            'pv_terminal': pv_terminal,
            'fcf_projections': fcf_projections,
            'terminal_value': terminal_value
        }
    
    def run_sensitivity_analysis(self) -> Dict:
        """민감도 분석"""
        scenarios = {
            'base': self.calculate_enterprise_value()['enterprise_value'],
            'optimistic': None,
            'pessimistic': None
        }
        
        # 낙관적 시나리오 (성장률 +2%p)
        original_growth = self.growth_rate
        self.growth_rate += 0.02
        scenarios['optimistic'] = self.calculate_enterprise_value()['enterprise_value']
        
        # 비관적 시나리오 (성장률 -2%p)
        self.growth_rate = original_growth - 0.02
        scenarios['pessimistic'] = self.calculate_enterprise_value()['enterprise_value']
        
        # 복구
        self.growth_rate = original_growth
        
        return scenarios
```

### 1.2 엑셀 생성기 (Python)

```python
# backend/app/services/excel_generator.py

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.chart import LineChart, Reference

class DCFExcelGenerator:
    """DCF 평가 결과를 엑셀로 출력"""
    
    def __init__(self, evaluation_data: Dict):
        self.data = evaluation_data
        self.wb = Workbook()
        
    def create_summary_sheet(self):
        """요약 시트"""
        ws = self.wb.active
        ws.title = "요약"
        
        # 헤더
        ws['A1'] = "DCF 기업가치평가 보고서"
        ws['A1'].font = Font(size=16, bold=True)
        
        # 주요 결과
        ws['A3'] = "평가 결과"
        ws['A3'].font = Font(bold=True)
        ws['A4'] = "기업가치 (EV)"
        ws['B4'] = self.data['enterprise_value']
        ws['B4'].number_format = '#,##0'
        
        # 가정사항
        ws['A7'] = "주요 가정"
        ws['A7'].font = Font(bold=True)
        ws['A8'] = "성장률"
        ws['B8'] = f"{self.data['growth_rate']*100:.1f}%"
        ws['A9'] = "WACC"
        ws['B9'] = f"{self.data['wacc']*100:.1f}%"
        
    def create_fcf_sheet(self):
        """FCF 예측 시트"""
        ws = self.wb.create_sheet("FCF 예측")
        
        # 헤더
        ws['A1'] = "잉여현금흐름 예측"
        ws['A1'].font = Font(size=14, bold=True)
        
        # 연도별 FCF
        years = ['Year 1', 'Year 2', 'Year 3', 'Year 4', 'Year 5']
        for i, year in enumerate(years, start=2):
            ws.cell(row=3, column=i, value=year)
            ws.cell(row=4, column=i, value=self.data['fcf_projections'][i-2])
            ws.cell(row=4, column=i).number_format = '#,##0'
        
        # 차트 추가
        chart = LineChart()
        chart.title = "FCF 추이"
        data = Reference(ws, min_col=2, min_row=4, max_col=6, max_row=4)
        chart.add_data(data)
        ws.add_chart(chart, "A7")
        
    def create_calculator_sheet(self):
        """시뮬레이터 시트 (고객이 직접 수정 가능)"""
        ws = self.wb.create_sheet("계산기")
        
        ws['A1'] = "📊 DCF 시뮬레이터"
        ws['A1'].font = Font(size=14, bold=True)
        
        ws['A3'] = "입력 변수 (자유롭게 수정하세요!)"
        ws['A3'].font = Font(bold=True)
        ws['A3'].fill = PatternFill(start_color="FFF2CC", fill_type="solid")
        
        # 입력 변수
        ws['A5'] = "현재 매출"
        ws['B5'] = self.data['revenue_history'][-1]
        ws['B5'].number_format = '#,##0'
        
        ws['A6'] = "성장률"
        ws['B6'] = self.data['growth_rate']
        ws['B6'].number_format = '0.0%'
        
        ws['A7'] = "WACC"
        ws['B7'] = self.data['wacc']
        ws['B7'].number_format = '0.0%'
        
        # 자동 계산 (수식)
        ws['A10'] = "계산 결과"
        ws['A10'].font = Font(bold=True)
        
        ws['A11'] = "Year 1 FCF"
        ws['B11'] = "=B5*(1+B6)*0.15*0.78*0.85"  # 간소화 수식
        ws['B11'].number_format = '#,##0'
        
        # 주석
        ws['A15'] = "💡 Tip: 위 노란색 셀의 숫자를 바꾸면 자동으로 재계산됩니다!"
        ws['A15'].font = Font(color="0070C0")
        
    def generate(self, output_path: str):
        """엑셀 파일 생성"""
        self.create_summary_sheet()
        self.create_fcf_sheet()
        self.create_calculator_sheet()
        
        self.wb.save(output_path)
        return output_path
```

### 1.3 FastAPI 라우터

```python
# backend/app/routers/dcf.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/api/v1/dcf", tags=["DCF Evaluation"])

class DCFRequest(BaseModel):
    company_id: str
    revenue_history: List[float]
    ebit_margin: float
    tax_rate: float
    growth_rate: float
    terminal_growth: float
    wacc: float

@router.post("/evaluate")
async def evaluate_dcf(request: DCFRequest):
    """DCF 평가 실행"""
    try:
        # 1. DCF 계산
        evaluator = DCFEvaluator(request.dict())
        result = evaluator.calculate_enterprise_value()
        
        # 2. 엑셀 생성
        excel_gen = DCFExcelGenerator({
            **request.dict(),
            **result
        })
        excel_path = f"outputs/{request.company_id}_dcf.xlsx"
        excel_gen.generate(excel_path)
        
        # 3. DB 저장
        # (Supabase에 결과 저장 로직)
        
        return {
            "evaluation_id": "generated_uuid",
            "enterprise_value": result['enterprise_value'],
            "excel_url": f"https://storage.../{ excel_path}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

## 🎨 2. 상대가치 평가 시스템

### 2.1 상대가치 평가 로직

```python
# backend/app/services/comparable_evaluator.py

class ComparableEvaluator:
    """상대가치평가 엔진"""
    
    def __init__(self, company_metrics: Dict, comparable_data: List[Dict]):
        self.company = company_metrics
        self.comparables = comparable_data
        
    def calculate_multiples(self) -> Dict:
        """멀티플 계산"""
        # 유사기업 평균 멀티플
        avg_per = np.mean([c['market_cap'] / c['net_income'] 
                           for c in self.comparables])
        avg_pbr = np.mean([c['market_cap'] / c['book_value'] 
                           for c in self.comparables])
        avg_psr = np.mean([c['market_cap'] / c['revenue'] 
                           for c in self.comparables])
        
        # 대상 기업 적용
        per_value = self.company['net_income'] * avg_per
        pbr_value = self.company['book_value'] * avg_pbr
        psr_value = self.company['revenue'] * avg_psr
        
        return {
            'per_value': per_value,
            'pbr_value': pbr_value,
            'psr_value': psr_value,
            'average_value': np.mean([per_value, pbr_value, psr_value])
        }
```

---

## 🌐 3. 웹 시뮬레이터 (Next.js)

### 3.1 DCF 계산기 컴포넌트

```typescript
// frontend/components/simulator/DCFCalculator.tsx

'use client';

import { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';

export function DCFCalculator() {
  const [inputs, setInputs] = useState({
    revenue: 100,
    growthRate: 20,
    wacc: 10,
    terminalGrowth: 3
  });
  
  const [result, setResult] = useState<number | null>(null);
  
  const calculate = () => {
    // 간소화된 DCF 계산
    const fcf = inputs.revenue * 0.15; // 15% FCF 마진 가정
    const pv5years = fcf * ((1 - Math.pow(1 + inputs.growthRate/100, 5)) / 
                            (inputs.wacc/100 - inputs.growthRate/100));
    const terminalValue = (fcf * Math.pow(1 + inputs.growthRate/100, 5) * 
                           (1 + inputs.terminalGrowth/100)) / 
                          (inputs.wacc/100 - inputs.terminalGrowth/100);
    const pv_terminal = terminalValue / Math.pow(1 + inputs.wacc/100, 5);
    
    const ev = pv5years + pv_terminal;
    setResult(Math.round(ev));
  };
  
  return (
    <Card>
      <CardHeader>
        <CardTitle>DCF 간이 계산기</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <label>현재 연매출 (억원)</label>
          <Input 
            type="number" 
            value={inputs.revenue}
            onChange={(e) => setInputs({...inputs, revenue: Number(e.target.value)})}
          />
        </div>
        
        <div>
          <label>연평균 성장률 (%)</label>
          <Input 
            type="number" 
            value={inputs.growthRate}
            onChange={(e) => setInputs({...inputs, growthRate: Number(e.target.value)})}
          />
        </div>
        
        <div>
          <label>할인율 (WACC) (%)</label>
          <Input 
            type="number" 
            value={inputs.wacc}
            onChange={(e) => setInputs({...inputs, wacc: Number(e.target.value)})}
          />
        </div>
        
        <div>
          <label>영구 성장률 (%)</label>
          <Input 
            type="number" 
            value={inputs.terminalGrowth}
            onChange={(e) => setInputs({...inputs, terminalGrowth: Number(e.target.value)})}
          />
        </div>
        
        <Button onClick={calculate} className="w-full">
          계산하기
        </Button>
        
        {result && (
          <div className="p-4 bg-green-50 rounded-lg">
            <p className="text-lg font-bold">
              기업가치: 약 {result.toLocaleString()} 억원
            </p>
            <p className="text-sm text-gray-600 mt-2">
              ⚠️ 이것은 간이 계산입니다. 정확한 평가는 전문 서비스를 이용하세요.
            </p>
            <Button variant="outline" className="mt-4">
              정식 평가 신청하기 →
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
```

---

## 🚀 4. 배포 가이드

### 4.1 Supabase 설정

```sql
-- Supabase에서 실행할 SQL

-- 1. 테이블 생성 (SQLAlchemy 모델 기반)
CREATE TABLE companies (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT NOT NULL,
  business_number TEXT UNIQUE NOT NULL,
  industry TEXT,
  established_date DATE,
  ceo TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE evaluations (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  company_id UUID REFERENCES companies(id),
  evaluation_type TEXT NOT NULL,
  evaluation_date DATE NOT NULL,
  status TEXT DEFAULT 'REQUESTED',
  enterprise_value NUMERIC,
  equity_value NUMERIC,
  excel_file_path TEXT,
  pdf_file_path TEXT,
  input_data JSONB,
  assumptions JSONB,
  results JSONB,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

### 4.2 환경 변수 (.env)

```bash
# .env.local (프론트엔드)
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJxxx...

# .env (백엔드)
DATABASE_URL=postgresql://xxx:xxx@xxx.supabase.co:5432/postgres
ANTHROPIC_API_KEY=sk-ant-xxx
SUPABASE_SERVICE_KEY=eyJxxx...
```

### 4.3 Vercel 배포

```bash
# 프론트엔드 배포
cd frontend
vercel --prod

# 백엔드는 Vercel Serverless Functions로 배포
# 또는 Railway/Render로 별도 배포
```

---

## ✅ 개발 체크리스트

### Week 1: 기초 설정
- [ ] Next.js 프로젝트 초기화
- [ ] Supabase 프로젝트 생성 및 DB 스키마 설정
- [ ] Tailwind + shadcn/ui 설정
- [ ] FastAPI 백엔드 기본 구조
- [ ] SQLAlchemy 설정

### Week 2: DCF 평가 시스템
- [ ] DCF 계산 로직 구현
- [ ] 엑셀 생성기 구현
- [ ] FastAPI 엔드포인트 구현
- [ ] 단위 테스트
- [ ] DCF 평가 신청 페이지 (프론트)

### Week 3: 상대가치 + 시뮬레이터
- [ ] 상대가치 평가 로직
- [ ] 상대가치 평가 엑셀 생성
- [ ] DCF 계산기 (React)
- [ ] 상대가치 계산기 (React)
- [ ] 상증법 계산기 (React)

### Week 4: 완성 및 배포
- [ ] 메인 페이지 완성
- [ ] YouTube 임베딩
- [ ] 전체 테스트
- [ ] Vercel 배포
- [ ] 도메인 연결 (valuation.ai.kr)
- [ ] 런칭! 🚀

---

## 📚 참고 자료

### DCF 이론
- 할인율(WACC) 계산 공식
- FCF 산출 방법
- Terminal Value 계산 (Gordon Growth Model)

### 엑셀 라이브러리
```bash
# Python
pip install openpyxl
pip install xlsxwriter

# 차트, 서식, 수식 모두 지원
```

### Next.js 참고
- App Router 사용
- Server Components vs Client Components
- API Routes

---

## 🎯 최종 목표

**4주 내에 첫 번째 고객 확보!**

MVP 기능:
1. ✅ DCF 평가 신청 및 자동 처리
2. ✅ 상대가치 평가 신청
3. ✅ 엑셀 파일 생성 및 제공 (고객이 직접 수정 가능)
4. ✅ 3종 웹 시뮬레이터
5. ✅ 메인 페이지 + YouTube 콘텐츠

---

## 💡 Claude Code에게 전달할 첫 번째 명령

```
이 작업지시서를 바탕으로:
1. 프로젝트 초기 설정해줘 (Next.js + FastAPI + Supabase)
2. 데이터베이스 스키마부터 만들어줘
3. DCF 평가 로직 구현해줘
4. DCF 엑셀 생성기 만들어줘
5. 웹 시뮬레이터(DCF 계산기) 만들어줘
```

---

**글자수: 12,847자 / 작성자: Claude / 프롬프터: 써니**
