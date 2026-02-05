# S4E2 Verification

## 검증 대상

- **Task ID**: S4E2
- **Task Name**: 뉴스 파서 및 데이터 추출
- **Stage**: S4 (External Integration - 개발 3차)
- **Area**: E (External)

## 검증자

**Verification Agent**: code-reviewer

---

## 검증 체크리스트

### 1. 빌드 & 컴파일 (최우선)

- [ ] **TypeScript 빌드 성공** (`npm run type-check`)
- [ ] **Next.js 빌드 성공** (`npm run build`)
- [ ] **ESLint 경고 0개** (`npm run lint`)

---

### 2. 파일 생성 확인

- [ ] **`lib/crawler/news-parser.ts` 존재** - 뉴스 파서

---

### 3. 핵심 기능 테스트

#### 3.1 인터페이스 정의

- [ ] **ParsedDealInfo 인터페이스**
  - company_name (string, 필수)
  - investment_stage? (string, optional)
  - investment_amount? (string, optional)
  - investors (string[], 필수)
  - industry? (string, optional)
  - location? (string, optional)

- [ ] **ParsedArticle 인터페이스**
  - title (string)
  - content (string)
  - published_date (string)
  - deal_info? (ParsedDealInfo, optional)

#### 3.2 NewsParser 클래스

- [ ] **parseArticle() 메서드**
  - HTML 문자열을 입력받음
  - CSS 선택자 객체 (title, content, date) 입력받음
  - Cheerio로 HTML 파싱
  - title, content, date 추출
  - parseDate()로 날짜 파싱
  - extractDealInfo()로 Deal 정보 추출
  - ParsedArticle 반환

- [ ] **extractDealInfo() 메서드 (private)**
  - 투자 키워드 확인 ('투자', '유치', '시리즈', '시드', '라운드', '펀딩')
  - 키워드가 없으면 undefined 반환
  - 기업명 추출 (extractCompanyName)
  - 투자단계 추출 (extractInvestmentStage)
  - 투자금액 추출 (extractInvestmentAmount)
  - 투자자 추출 (extractInvestors)
  - 업종 추출 (extractIndustry)
  - 지역 추출 (extractLocation)
  - ParsedDealInfo 반환

#### 3.3 개별 추출 함수

- [ ] **extractCompanyName() (private)**
  - 패턴: "스타트업 XXX", "XXX는", "XXX가", "XXX(대표...)"
  - 정규표현식 매칭
  - 일반 명사 제외 ('투자', '금액', '규모', '회사', '업체', '서비스')
  - 첫 번째 매칭 반환

- [ ] **extractInvestmentStage() (private)**
  - 키워드 목록: 시드, 프리A, 프리시리즈A, 시리즈A~E, 브릿지, Series A~C
  - text.includes() 확인
  - 정규화: '프리시리즈A' → '프리A', 'Series A' → '시리즈A'

- [ ] **extractInvestmentAmount() (private)**
  - 패턴: "100억원", "50억 규모", "$10M", "1000만 달러"
  - 정규표현식 매칭
  - 공백 정리 (trim)

- [ ] **extractInvestors() (private)**
  - 유명 VC 리스트 확인 (알토스벤처스, 삼성벤처투자 등)
  - 패턴: "~로부터", "~에게서", "벤처스", "인베스트먼트", "투자", "캐피탈"
  - 중복 제거
  - 배열 반환

- [ ] **extractIndustry() (private)**
  - 키워드 목록: AI, 인공지능, 헬스케어, 의료, 핀테크 등
  - 정규화: '인공지능' → 'AI', '의료' → '헬스케어'

- [ ] **extractLocation() (private)**
  - 키워드 목록: 판교, 강남, 서울, 부산, 대구 등
  - text.includes() 확인

- [ ] **parseDate() (private)**
  - ISO 형식 (YYYY-MM-DD): 그대로 반환
  - 점 형식 (YYYY.MM.DD): ISO로 변환
  - 한글 형식 (M월 D일): 현재 연도 + ISO 변환
  - 파싱 실패: 현재 날짜 반환

#### 3.4 일괄 파싱

- [ ] **parseArticles() 메서드**
  - HTML 목록 (배열) 입력
  - 각 HTML에 대해 parseArticle() 호출
  - ParsedArticle 배열 반환

#### 3.5 싱글톤 인스턴스

- [ ] **newsParser 인스턴스**
  - `export const newsParser = new NewsParser()`

---

### 4. 통합 테스트

#### 4.1 선행 Task 연동

- [ ] **S4E1 (Base Crawler)**
  - BaseCrawler에서 HTML 가져오기
  - newsParser.parseArticle() 호출
  - CrawlResult 생성

#### 4.2 정규표현식 패턴 테스트

**기업명 추출 테스트:**
```typescript
const text1 = "스타트업 테크이노가 100억원 투자 유치"
// → "테크이노"

const text2 = "테크이노(대표 김철수)는 투자를 유치했다"
// → "테크이노"

const text3 = "AI 스타트업 테크이노는 투자를 유치했다"
// → "테크이노"
```

**투자금액 추출 테스트:**
```typescript
const text1 = "100억원 규모의 투자"
// → "100억원"

const text2 = "$10M 투자 유치"
// → "$10M"

const text3 = "1000만 달러"
// → "1000만 달러"
```

**투자자 추출 테스트:**
```typescript
const text1 = "알토스벤처스와 삼성벤처투자로부터 투자 유치"
// → ["알토스벤처스", "삼성벤처투자"]

const text2 = "KB인베스트먼트의 투자"
// → ["KB인베스트먼트"]
```

- [ ] **모든 패턴 테스트 통과**

#### 4.3 날짜 파싱 테스트

```typescript
parseDate("2026-02-06") // → "2026-02-06"
parseDate("2026.02.06") // → "2026-02-06"
parseDate("2월 6일")     // → "2026-02-06"
parseDate("invalid")    // → 현재 날짜 (YYYY-MM-DD)
```

- [ ] **모든 날짜 형식 테스트 통과**

---

### 5. Blocker 확인

- [ ] **의존성 차단**
  - S4E1 (Base Crawler) 완료 확인

- [ ] **환경 차단**
  - 없음 (Cheerio만 사용)

- [ ] **외부 API 차단**
  - 없음

---

## 합격 기준

### 필수 (Must Pass)

1. **빌드 성공** ✅
2. **파일 생성 완료** ✅
3. **parseArticle() 구현** ✅
4. **extractDealInfo() 구현** ✅
5. **개별 추출 함수 모두 구현** ✅ (6개)
6. **정규표현식 패턴 테스트 통과** ✅
7. **날짜 파싱 테스트 통과** ✅

### 권장 (Nice to Pass)

1. **AI 기반 정보 추출** ✨ (Claude API)
2. **추출 정확도 개선** ✨
3. **추가 필드 추출** ✨ (직원수, 설립일)

---

## 검증 결과

**Status**: [ ] Pass / [ ] Fail

---

## 주의사항

1. **정규표현식 패턴**
   - 다양한 형식 지원
   - 한글/영문 혼용 처리
   - 일반 명사 제외 필수

2. **투자자 추출**
   - 유명 VC 리스트 활용
   - 패턴 매칭 보완
   - 중복 제거

3. **날짜 파싱**
   - 다양한 날짜 형식 지원
   - 파싱 실패 시 현재 날짜 반환
   - padStart()로 2자리 포맷

4. **정규화**
   - "인공지능" → "AI"
   - "Series A" → "시리즈A"
   - "프리시리즈A" → "프리A"

5. **에러 처리**
   - 파싱 실패 시 undefined 반환 (에러 발생 안 함)
   - 빈 문자열보다 null/undefined 선호

---

## PO 테스트 가이드

### 1. 기본 파싱 테스트

```typescript
import { newsParser } from '@/lib/crawler/news-parser'

const html = `
<html>
  <body>
    <h1 class="title">AI 스타트업 테크이노, 알토스벤처스로부터 100억원 시리즈A 투자 유치</h1>
    <div class="content">
      AI 기반 헬스케어 스타트업 테크이노(대표 김철수)가
      알토스벤처스와 삼성벤처투자로부터 100억원 규모의
      시리즈A 투자를 유치했다고 25일 밝혔다.
      판교에 본사를 둔 테크이노는 현재 직원 50명 규모다.
    </div>
    <span class="date">2026.02.06</span>
  </body>
</html>
`

const parsed = newsParser.parseArticle(html, {
  title: 'h1.title',
  content: 'div.content',
  date: 'span.date'
})

console.log(parsed)
// 기대 결과:
// {
//   title: "AI 스타트업 테크이노, 알토스벤처스로부터 100억원 시리즈A 투자 유치",
//   content: "AI 기반 헬스케어 스타트업 테크이노...",
//   published_date: "2026-02-06",
//   deal_info: {
//     company_name: "테크이노",
//     investment_stage: "시리즈A",
//     investment_amount: "100억원",
//     investors: ["알토스벤처스", "삼성벤처투자"],
//     industry: "AI",
//     location: "판교"
//   }
// }
```

### 2. 투자 키워드 없는 경우

```typescript
const html = `
<html>
  <body>
    <h1>테크 뉴스: 새로운 서비스 출시</h1>
    <div>단순 뉴스 내용</div>
    <span>2026.02.06</span>
  </body>
</html>
`

const parsed = newsParser.parseArticle(html, {
  title: 'h1',
  content: 'div',
  date: 'span'
})

console.log(parsed.deal_info) // → undefined
```

---

## 참조

- Task Instruction: `task-instructions/S4E2_instruction.md`
- 기존 프로토타입: `backend/app/services/news_parser.py`

---

**작성일**: 2026-02-06
**작성자**: Claude Code (Sonnet 4.5)
