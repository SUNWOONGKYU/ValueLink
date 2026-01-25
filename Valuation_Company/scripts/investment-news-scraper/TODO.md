# TODO - 투자 뉴스 스크래퍼 시스템

## 🔴 높은 우선순위

### 1. 투자 통계를 실제 Deal 테이블 데이터로 변경

**현재 상태:**
- Deal 페이지의 투자 통계가 뉴스 기사 수로 표시됨
- 어제/지난주/금년 투자유치 "기업 수"라고 표시하지만 실제로는 "기사 수"

**해야 할 작업:**
```sql
-- Deal 테이블 구조 (예상)
CREATE TABLE deals (
    id SERIAL PRIMARY KEY,
    company_name TEXT,
    investment_date DATE,
    investment_amount TEXT,
    investment_stage TEXT,
    investors TEXT,
    industry TEXT,
    region TEXT,
    employees TEXT
);
```

**변경 로직:**
```javascript
// 현재: 뉴스 기사 수 카운트
SELECT COUNT(*) FROM investment_news_articles
WHERE published_date = '2026-01-25'

// 변경 후: 실제 투자유치 기업 수 카운트
SELECT COUNT(DISTINCT company_name) FROM deals
WHERE investment_date = '2026-01-25'
```

**주의사항:**
- 중복 기업 제거 필요 (DISTINCT company_name)
- 같은 기업이 여러 라운드 투자받은 경우 1회만 카운트
- investment_date 필드 필수

**파일 위치:**
- `valuation-platform/frontend/app/deal.html` (833-845 라인)

---

## 🟡 중간 우선순위

### 2. Gemini API 자동화 스크립트 작성

**목표:** 매일 자동으로 Top 10 사이트에서 뉴스 수집

**필요 작업:**
1. Gemini API 키 설정 (.env에 이미 있음)
2. Python 스크립트 작성
   - Gemini API로 웹 스크래핑 요청
   - JSON 응답 받아서 파싱
   - Supabase 자동 저장
3. GitHub Actions 스케줄러 설정
   - 매일 오전 9시 실행
   - 에러 발생 시 알림

**참고:**
- `.claude/rules/08_article-selection.md` - 기사 선정 기준
- `scripts/investment-news-scraper/README.md` - Gemini CLI 섹션

---

### 3. 기사 선정 로직 구현

**목표:** 같은 기업의 여러 기사 중 Best 기사 1개만 선정

**기준 (점수 시스템):**
- 투자금액: 3점
- 투자자: 3점
- 투자단계: 2점
- 업종: 1점
- 지역: 1점
- 직원수: 1점
- 동점 시: 글자수 → 발행일 → 사이트랭킹

**필요 작업:**
1. NLP/키워드 추출 로직 작성
2. 점수 계산 함수
3. 같은 기업 기사 그룹핑
4. Best 기사 선정 및 Deal 테이블 저장

**참고:**
- `ARTICLE_SELECTION_CRITERIA.md` - 상세 기준

---

## 🟢 낮은 우선순위

### 4. Deal 테이블 자동 채우기

**워크플로우:**
```
1. 매일 Top 10 사이트에서 뉴스 수집
2. 기사 선정 로직으로 Best 기사 선정
3. 선정된 기사에서 필드 추출
4. Deal 테이블에 자동 INSERT
```

---

### 5. 통계 API 엔드포인트 생성

**목표:** 프론트엔드에서 실시간 통계 조회

**엔드포인트:**
```
GET /api/v1/investment-tracker/stats
Response:
{
  "yesterday": 5,
  "last_week": 23,
  "year_total": 156
}
```

---

### 6. 나머지 8개 사이트 처리

**제외된 사이트 (11-16위):**
- 뉴스톱 (21)
- 지디넷코리아 (15)
- 테크월드뉴스 (18)
- 매경MK테크 (24)
- 정책브리핑 (26)
- 모비인사이드 (14)

**수집 실패 사이트:**
- 넥스트유니콘 (17)
- 벤처경영신문 (20)
- 다음뉴스 (25)

**결정 필요:**
- Top 10에서 제외할지
- 또는 Selenium/다른 방법으로 수집할지

---

## 📝 완료된 작업

- ✅ Top 10 사이트 확정 및 랭킹 저장
- ✅ Deal 페이지 우측 사이드바 구현
- ✅ 기사 선정 기준 문서화 (3곳)
- ✅ Gemini CLI 통합 가이드
- ✅ 투자 통계 표시 (임시 데이터)
- ✅ 100건의 투자 뉴스 수집

---

## 📅 작업 일정 (예상)

| 작업 | 예상 소요 | 우선순위 |
|------|----------|----------|
| Deal 테이블 데이터로 통계 변경 | 1-2시간 | 🔴 높음 |
| Gemini API 자동화 | 3-4시간 | 🟡 중간 |
| 기사 선정 로직 구현 | 4-6시간 | 🟡 중간 |
| Deal 테이블 자동 채우기 | 2-3시간 | 🟢 낮음 |

---

**최종 업데이트:** 2026-01-26
**작성자:** Claude Code
