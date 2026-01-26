# 더브이씨(TheVC.kr) 활용 전략

> 투자사 데이터베이스 구축 및 Deal 정보 보강

---

## 1. 더브이씨란?

**사이트:** https://thevc.kr

**특징:**
- 한국 벤처캐피탈/투자사 디렉토리
- 투자사별 프로필, 포트폴리오, 연락처 제공
- 투자 뉴스가 아닌 **투자사 정보** 플랫폼

**분석 결과:**
- 투자 관련 키워드: 53개
- 캐피탈: 3개
- 벤처스: 5개
- VC: 7개

---

## 2. 활용 목적

### 목적 1: 투자자 정보 검증 및 보강 ⭐⭐⭐

**문제:**
```
Deal 테이블에 저장된 investors 필드:
- "알토스벤처스" (오타 가능)
- "알토스" (약칭)
- "Altos Ventures" (영문)
→ 표기가 통일되지 않음
```

**해결:**
```
TheVC.kr에서 공식 투자사 명칭 확인:
- 정식 명칭: "알토스벤처스"
- 영문명: "Altos Ventures"
- 웹사이트: https://www.altos.vc/
→ 통일된 표기로 저장
```

---

### 목적 2: 투자사 프로필 데이터베이스 구축 ⭐⭐

**저장할 정보:**
```sql
CREATE TABLE investors (
  id SERIAL PRIMARY KEY,
  vc_name TEXT UNIQUE,                -- 투자사명
  vc_name_en TEXT,                    -- 영문명
  website TEXT,                       -- 웹사이트
  contact_email TEXT,                 -- 이메일
  focus_industries TEXT[],            -- 관심 업종
  investment_stage TEXT[],            -- 투자 단계 (시드, 시리즈A 등)
  total_investments INTEGER,          -- 총 투자 건수
  profile_url TEXT,                   -- TheVC 프로필 URL
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

**활용:**
- Deal 테이블의 investors 필드와 조인
- 투자사별 포트폴리오 분석
- 업종별 주요 투자자 파악

---

### 목적 3: 투자 트렌드 분석 ⭐

**분석 가능 항목:**
```
1. 투자사별 투자 빈도
   - 알토스벤처스: 월 5건
   - KB인베스트먼트: 월 3건

2. 업종별 주요 투자자
   - AI: 알토스, KB, 삼성벤처
   - 헬스케어: DSC, SDB

3. 투자 단계별 투자자
   - 시드: 프라이머, 본엔젤스
   - 시리즈A: 알토스, KB
```

---

## 3. 데이터 수집 방법

### 방법 A: 투자사 목록 페이지 크롤링

**URL 패턴 분석:**
```
메인 페이지: https://thevc.kr
투자사 목록: https://thevc.kr/investors (예상)
개별 프로필: https://thevc.kr/투자사명 (예상)
```

**수집 프로세스:**
```python
def collect_vc_list():
    """투자사 목록 수집"""
    url = 'https://thevc.kr'
    soup = BeautifulSoup(requests.get(url).content, 'html.parser')

    # 투자사 링크 찾기
    vc_links = soup.select('a[href*="thevc.kr/"]')

    investors = []
    for link in vc_links:
        vc_url = link['href']
        vc_name = link.text.strip()

        if vc_name and '투자' in vc_name or 'VC' in vc_name:
            investors.append({
                'name': vc_name,
                'url': vc_url
            })

    return investors
```

---

### 방법 B: 개별 투자사 페이지 상세 수집

**수집할 정보:**
```python
def scrape_vc_profile(vc_url):
    """투자사 프로필 상세 정보 수집"""
    soup = BeautifulSoup(requests.get(vc_url).content, 'html.parser')

    return {
        'name': soup.select_one('.vc-name').text,
        'website': soup.select_one('.vc-website')['href'],
        'email': soup.select_one('.vc-email').text,
        'focus_industries': [tag.text for tag in soup.select('.vc-industry')],
        'investment_stage': [tag.text for tag in soup.select('.vc-stage')],
    }
```

---

## 4. Deal 정보 보강 프로세스

### 현재 프로세스 (투자 뉴스만)

```
뉴스 수집 → Gemini 추출 → Deal 저장
                ↓
    investors: "알토스" (불명확)
```

### 개선된 프로세스 (투자사 DB 활용)

```
뉴스 수집 → Gemini 추출 → 투자사 검증 → Deal 저장
                ↓              ↓
    investors: "알토스"   TheVC DB 조회
                            ↓
                investors: "알토스벤처스" (정식명칭)
                website: "https://www.altos.vc/"
                vc_id: 42
```

**구현 코드:**
```python
def validate_investor_name(investor_name):
    """투자사 이름 검증 및 정규화"""

    # TheVC DB에서 조회
    result = supabase.table('investors').select('*').ilike('vc_name', f'%{investor_name}%').execute()

    if result.data:
        # 정식 명칭으로 교체
        return result.data[0]['vc_name']
    else:
        # DB에 없으면 원본 유지
        return investor_name


def enrich_deal_with_investor_info(deal):
    """Deal에 투자사 정보 추가"""

    investors = deal['investors'].split(', ')
    validated_investors = []
    investor_ids = []

    for inv in investors:
        validated_name = validate_investor_name(inv)
        validated_investors.append(validated_name)

        # 투자사 ID 조회
        result = supabase.table('investors').select('id').eq('vc_name', validated_name).execute()
        if result.data:
            investor_ids.append(result.data[0]['id'])

    deal['investors'] = ', '.join(validated_investors)
    deal['investor_ids'] = investor_ids

    return deal
```

---

## 5. 투자사 DB 구축 단계

### Phase 1: 기본 DB 구축 (1주)

**목표:** 주요 투자사 100개 수집

**작업:**
1. TheVC.kr 투자사 목록 크롤링
2. 투자사명, 웹사이트, 이메일 수집
3. `investors` 테이블 생성 및 저장

**예상 결과:**
```
100개 투자사 DB
- 알토스벤처스
- KB인베스트먼트
- 삼성벤처투자
- ...
```

---

### Phase 2: 상세 정보 보강 (2주)

**목표:** 투자사별 상세 프로필 수집

**작업:**
1. 개별 투자사 페이지 크롤링
2. 관심 업종, 투자 단계 수집
3. 포트폴리오 정보 수집

**예상 결과:**
```
알토스벤처스:
- 관심 업종: AI, 커머스, SaaS
- 투자 단계: 시리즈A, 시리즈B
- 포트폴리오: 배달의민족, 당근마켓, ...
```

---

### Phase 3: Deal 연동 (3주)

**목표:** 기존 Deal 데이터와 투자사 DB 연결

**작업:**
1. 기존 Deal의 investors 필드 정규화
2. `investor_ids` 필드 추가 (배열)
3. Deal-Investor 관계 설정

**예상 결과:**
```sql
SELECT d.company_name, d.amount, i.vc_name, i.website
FROM deals d
JOIN deal_investors di ON d.id = di.deal_id
JOIN investors i ON di.investor_id = i.id
WHERE i.vc_name = '알토스벤처스';
```

---

## 6. 활용 시나리오

### 시나리오 1: 투자자 자동 완성

**사용자 입력:** "알토"
**시스템 제안:**
- 알토스벤처스 (Altos Ventures)
- 알바트로스인베스트먼트

### 시나리오 2: 투자사별 포트폴리오

**쿼리:** "알토스벤처스가 투자한 기업"
**결과:**
```
1. 배달의민족 - 300억원 (시리즈C)
2. 당근마켓 - 200억원 (시리즈B)
3. 마켓컬리 - 150억원 (시리즈A)
...
```

### 시나리오 3: 업종별 투자자 추천

**쿼리:** "AI 스타트업에 투자하는 주요 투자사"
**결과:**
```
1. 알토스벤처스 (15건)
2. KB인베스트먼트 (12건)
3. 삼성벤처투자 (10건)
```

---

## 7. 기술 구현

### 투자사 테이블 스키마

```sql
CREATE TABLE investors (
  id SERIAL PRIMARY KEY,
  vc_name TEXT UNIQUE NOT NULL,
  vc_name_en TEXT,
  website TEXT,
  contact_email TEXT,
  phone TEXT,
  address TEXT,
  focus_industries TEXT[],
  investment_stage TEXT[],
  total_investments INTEGER DEFAULT 0,
  portfolio_companies TEXT[],
  profile_url TEXT,
  thevc_url TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Deal과 Investor 다대다 관계
CREATE TABLE deal_investors (
  deal_id INTEGER REFERENCES deals(id),
  investor_id INTEGER REFERENCES investors(id),
  PRIMARY KEY (deal_id, investor_id)
);
```

### 크롤링 스크립트

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TheVC.kr 투자사 정보 수집
"""

import requests
from bs4 import BeautifulSoup
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)


def collect_investors():
    """투자사 목록 수집"""

    url = 'https://thevc.kr'
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(response.content, 'html.parser')

    # 투자사 링크 찾기 (실제 선택자는 사이트 구조에 따라 수정 필요)
    vc_elements = soup.select('a[href*="thevc.kr/"]')

    investors = []
    for elem in vc_elements:
        vc_name = elem.text.strip()
        vc_url = elem['href']

        if vc_name and len(vc_name) > 1:
            investors.append({
                'vc_name': vc_name,
                'thevc_url': vc_url
            })

    return investors


def save_investors(investors):
    """투자사 정보 저장"""

    for investor in investors:
        try:
            # 중복 체크
            existing = supabase.table('investors').select('id').eq('vc_name', investor['vc_name']).execute()

            if not existing.data:
                # 새 투자사 저장
                supabase.table('investors').insert(investor).execute()
                print(f"[SAVED] {investor['vc_name']}")
            else:
                print(f"[SKIP] {investor['vc_name']} already exists")

        except Exception as e:
            print(f"[ERROR] {investor['vc_name']}: {e}")


if __name__ == '__main__':
    print("TheVC.kr 투자사 정보 수집 시작")

    investors = collect_investors()
    print(f"수집된 투자사: {len(investors)}개")

    save_investors(investors)
    print("완료")
```

---

## 8. 예상 효과

### Before (투자사 DB 없음)

```
Deal 테이블:
- investors: "알토스" (불명확)
- 투자사 검증 불가
- 중복 표기 (알토스, 알토스벤처스, Altos)
```

### After (투자사 DB 활용)

```
Deal 테이블:
- investors: "알토스벤처스" (정식 명칭)
- investor_ids: [42]
- 투자사 정보 연결 가능

투자사 DB:
- 100+ 투자사 프로필
- 업종별/단계별 필터링
- 포트폴리오 분석
```

---

## 9. 다음 단계

### 즉시 실행 (오늘)

1. ✅ **Supabase에 investors 테이블 생성**
2. ✅ **TheVC.kr 크롤링 테스트**
3. ✅ **주요 투자사 10개 수동 입력** (테스트용)

### 단기 (1주일)

4. ✅ **투자사 자동 수집 스크립트 완성**
5. ✅ **100개 투자사 DB 구축**
6. ✅ **Deal 저장 시 투자사 검증 로직 추가**

### 중기 (2-3주)

7. ✅ **투자사 상세 프로필 수집**
8. ✅ **Deal-Investor 관계 설정**
9. ✅ **투자사별 포트폴리오 대시보드**

---

## 요약

**더브이씨 활용 전략:**
1. 🎯 **목적:** 투자사 DB 구축 (투자 뉴스 X)
2. 📊 **수집 정보:** 투자사명, 웹사이트, 관심 업종, 투자 단계
3. 🔗 **연동:** Deal 테이블의 investors 검증 및 정규화
4. 📈 **효과:** 투자자 데이터 품질 향상, 트렌드 분석 가능
5. ⏱️ **일정:** 3주 (기본 DB → 상세 정보 → Deal 연동)
