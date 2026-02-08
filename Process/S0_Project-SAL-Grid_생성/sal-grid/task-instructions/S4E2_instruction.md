# S4E2: News Parser & Data Extraction (신규 구현)

## Task 정보

- **Task ID**: S4E2
- **Task Name**: 뉴스 파서 및 데이터 추출 구현
- **Stage**: S4 (External Integration - 개발 3차)
- **Area**: E (External)
- **Dependencies**: S4E1 (Base Crawler)
- **Task Agent**: backend-developer
- **Verification Agent**: code-reviewer

---

## Task 목표

**HTML에서 투자 뉴스 데이터를 추출하고 Deal 정보를 파싱하는 파서 구현**

- Cheerio로 HTML 파싱
- 정규표현식으로 투자 정보 추출
- 기업명, 투자 단계, 투자 금액, 투자자, 업종, 지역 추출
- **4가지 측면에서 구현** (정확성, 성능, 코드 품질, 확장성)

---

## 🎯 구현 필수 영역 (4가지)

### 1️⃣ 추출 정확성 (Accuracy)
- ✅ 정규표현식 패턴 정확히 구현
- ✅ 다양한 형식 지원 (한글/영문 혼용)
- ✅ 일반 명사 제외 (기업명 추출 시)
- ✅ 정규화 (Series A → 시리즈A)

### 2️⃣ 성능 최적화 (Performance)
- ✅ 정규표현식 컴파일 최적화
- ✅ 불필요한 배열 복사 방지
- ✅ 조기 종료 (패턴 매칭 시)
- ✅ 일괄 파싱 지원 (배열 처리)

### 3️⃣ 코드 품질 향상 (Code Quality)
- ✅ TypeScript strict mode 준수
- ✅ JSDoc 주석 (정규표현식 패턴 설명)
- ✅ 명확한 함수명 (extractXXX)
- ✅ 에러 핸들링 강화

### 4️⃣ 확장성 (Extensibility)
- ✅ 새 패턴 추가 용이
- ✅ 유명 VC 리스트 확장 가능
- ✅ 업종 목록 확장 가능
- ✅ 날짜 형식 확장 가능

---

## 작업 방식

### Step 1: HTML 파싱 라이브러리

**Cheerio 사용:**
- jQuery-like API
- 서버 사이드에서 빠른 파싱
- CSS 선택자 지원

**핵심 메서드:**
```typescript
const $ = cheerio.load(html)
const title = $('h1.article-title').text().trim()
const content = $('.article-body').text().trim()
```

### Step 2: 정규표현식 패턴 설계

**주요 추출 항목:**

```
1. 기업명
   - 패턴: "스타트업 XXX", "XXX(대표 OOO)"
   - 제외: 일반 명사 (투자, 금액, 규모 등)

2. 투자 단계
   - 패턴: 시드, 프리A, 시리즈A, Series A
   - 정규화: Series A → 시리즈A

3. 투자 금액
   - 패턴: "100억원", "$10M", "50억 규모"

4. 투자자
   - 유명 VC 리스트 매칭
   - 패턴: "~로부터", "~의 투자"

5. 업종
   - 패턴: AI, 헬스케어, 핀테크 등
   - 정규화: 인공지능 → AI

6. 지역
   - 패턴: 판교, 강남, 서울 등
```

### Step 3: 구현 사항 적용

**예시 1: 기업명 추출**

```typescript
// ❌ 단순 구현: 일반 명사 포함
function extractCompanyName(text: string): string | null {
  const match = text.match(/([가-힣A-Za-z0-9]+)는/)
  return match ? match[1] : null
}

// ✅ 개선: 일반 명사 제외 + 복수 패턴
private extractCompanyName(text: string): string | null {
  // 패턴: "스타트업 XXX", "XXX(대표 OOO)", "XXX는"
  const patterns = [
    /스타트업\s+([가-힣A-Za-z0-9]+)/,
    /기업\s+([가-힣A-Za-z0-9]+)/,
    /([가-힣A-Za-z0-9]{2,10})\(대표[^)]+\)/,
    /([가-힣A-Za-z0-9]{2,10})[은는이가]/,
  ]

  for (const pattern of patterns) {
    const match = text.match(pattern)
    if (match && match[1]) {
      // 일반 명사 제외
      const commonNouns = ['투자', '금액', '규모', '회사', '업체', '서비스']
      if (!commonNouns.includes(match[1])) {
        return match[1]
      }
    }
  }

  return null
}
```

**예시 2: 투자자 추출**

```typescript
// ❌ 단순 구현: 하드코딩된 VC만
function extractInvestors(text: string): string[] {
  if (text.includes('알토스벤처스')) return ['알토스벤처스']
  return []
}

// ✅ 개선: VC 리스트 + 패턴 매칭
private extractInvestors(text: string): string[] {
  const investors: string[] = []

  // 유명 VC 리스트
  const knownVCs = [
    '알토스벤처스',
    '삼성벤처투자',
    'KB인베스트먼트',
    '카카오벤처스',
    '스마일게이트인베스트먼트',
    '본엔젤스',
    '프라이머',
    'DSC인베스트먼트',
    '퓨처플레이',
    '소프트뱅크벤처스',
  ]

  // 유명 VC 매칭
  for (const vc of knownVCs) {
    if (text.includes(vc)) {
      investors.push(vc)
    }
  }

  // 패턴: "~로부터", "~에게서", "~의 투자"
  const investorPatterns = [
    /([가-힣A-Za-z0-9]+(?:벤처스|인베스트먼트|투자|캐피탈))[으로]?부터/g,
    /([가-힣A-Za-z0-9]+(?:벤처스|인베스트먼트|투자|캐피탈))[에게]?서/g,
  ]

  for (const pattern of investorPatterns) {
    const matches = text.matchAll(pattern)
    for (const match of matches) {
      if (match[1] && !investors.includes(match[1])) {
        investors.push(match[1])
      }
    }
  }

  return investors
}
```

**예시 3: 날짜 파싱**

```typescript
// ❌ 단순 구현: 한 가지 형식만
function parseDate(dateText: string): string {
  return dateText.split('.').join('-')
}

// ✅ 개선: 다양한 형식 지원
private parseDate(dateText: string): string {
  // ISO 형식이면 그대로 반환
  if (/^\d{4}-\d{2}-\d{2}/.test(dateText)) {
    return dateText.split('T')[0]
  }

  // "2026.02.05" 형식
  const dotMatch = dateText.match(/(\d{4})\.(\d{1,2})\.(\d{1,2})/)
  if (dotMatch) {
    const [, year, month, day] = dotMatch
    return `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`
  }

  // "2월 5일" 형식 (현재 연도 사용)
  const koreanMatch = dateText.match(/(\d{1,2})월\s*(\d{1,2})일/)
  if (koreanMatch) {
    const [, month, day] = koreanMatch
    const year = new Date().getFullYear()
    return `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`
  }

  // 파싱 실패 시 현재 날짜
  return new Date().toISOString().split('T')[0]
}
```

**예시 4: Deal 정보 추출 (투자 관련 기사 필터링)**

```typescript
// ❌ 단순 구현: 모든 기사 파싱
function extractDealInfo(text: string): ParsedDealInfo {
  return {
    company_name: extractCompanyName(text) || '',
    // ...
  }
}

// ✅ 개선: 투자 관련 기사만 파싱
private extractDealInfo(text: string): ParsedDealInfo | undefined {
  // 투자 관련 키워드가 없으면 null
  const investmentKeywords = ['투자', '유치', '시리즈', '시드', '라운드', '펀딩']
  const hasInvestmentKeyword = investmentKeywords.some((keyword) =>
    text.includes(keyword)
  )

  if (!hasInvestmentKeyword) {
    return undefined
  }

  return {
    company_name: this.extractCompanyName(text) || '',
    investment_stage: this.extractInvestmentStage(text),
    investment_amount: this.extractInvestmentAmount(text),
    investors: this.extractInvestors(text),
    industry: this.extractIndustry(text),
    location: this.extractLocation(text),
  }
}
```

### Step 4: Best Practice 적용

**TypeScript 타입 정의:**
```typescript
// ✅ 파싱된 Deal 정보
export interface ParsedDealInfo {
  company_name: string
  investment_stage?: string
  investment_amount?: string
  investors: string[]
  industry?: string
  location?: string
}

// ✅ 파싱된 기사
export interface ParsedArticle {
  title: string
  content: string
  published_date: string
  deal_info?: ParsedDealInfo
}
```

**싱글톤 패턴:**
```typescript
export class NewsParser {
  // ...
}

export const newsParser = new NewsParser()
```

---

## 전제조건 확인

**S4E1 완료 확인:**
- BaseCrawler 구현됨
- CrawlResult 타입 정의됨

---

## 생성 파일 (1개)

### lib/crawler/news-parser.ts
**목표:** 뉴스 파서

**포함 메서드:**
1. **parseArticle()**: HTML에서 기사 파싱
2. **extractDealInfo()**: Deal 정보 추출
3. **extractCompanyName()**: 기업명 추출
4. **extractInvestmentStage()**: 투자 단계 추출
5. **extractInvestmentAmount()**: 투자 금액 추출
6. **extractInvestors()**: 투자자 추출
7. **extractIndustry()**: 업종 추출
8. **extractLocation()**: 지역 추출
9. **parseDate()**: 날짜 파싱
10. **parseArticles()**: 여러 기사 일괄 파싱

**개선 사항:**
- ✅ 다양한 정규표현식 패턴
- ✅ 일반 명사 제외
- ✅ 정규화 (Series A → 시리즈A)
- ✅ 투자 관련 기사 필터링

---

## 완료 기준

### 필수 (Must Have)
- [ ] NewsParser 클래스 구현
- [ ] parseArticle() 메서드
- [ ] 기업명 추출
- [ ] 투자 단계 추출
- [ ] 투자 금액 추출
- [ ] 투자자 추출
- [ ] 업종 추출
- [ ] 날짜 파싱
- [ ] 일괄 파싱 (parseArticles)

### 검증 (Verification)
- [ ] TypeScript 빌드 성공
- [ ] ESLint 에러 0개
- [ ] Cheerio 파싱 동작 확인
- [ ] 정규표현식 패턴 테스트
- [ ] 다양한 날짜 형식 파싱 확인

### 구현 항목 (Implementation)
- [ ] 정확성: 정규표현식 패턴, 일반 명사 제외
- [ ] 성능: 정규표현식 최적화, 조기 종료
- [ ] 코드 품질: JSDoc, 명확한 함수명
- [ ] 확장성: 패턴 추가 용이, VC 리스트 확장

---

## 참조

### 정규표현식 패턴

**기업명:**
- `스타트업\s+([가-힣A-Za-z0-9]+)`
- `([가-힣A-Za-z0-9]{2,10})\(대표[^)]+\)`

**투자 금액:**
- `(\d+(?:,\d+)?억\s*원?)`
- `(\$\d+(?:\.\d+)?M)`

**투자자:**
- `([가-힣A-Za-z0-9]+(?:벤처스|인베스트먼트))[으로]?부터`

### 관련 Task
- **S4E1**: Base Crawler (CrawlResult 타입)
- **S4E3**: Site-Specific Crawlers (파서 사용)

---

## 주의사항

### 🔍 정확성

1. **일반 명사 제외**
   - 기업명 추출 시 "투자", "금액" 등 제외
   - commonNouns 리스트 활용

2. **정규화**
   - "인공지능" → "AI"
   - "Series A" → "시리즈A"

### ⚡ 성능

1. **정규표현식 최적화**
   - 조기 종료 (패턴 매칭 시)
   - 불필요한 배열 복사 방지

2. **일괄 파싱**
   - parseArticles() 메서드로 배열 처리

### 📝 코드 품질

1. **JSDoc 주석**
   - 정규표현식 패턴 설명
   - 파라미터/반환값 설명

2. **명확한 함수명**
   - extractCompanyName (동사 + 명사)
   - parseDate (간결)

---

## 예상 소요 시간

**작업 복잡도**: Medium
**파일 수**: 1개
**라인 수**: ~300줄

---

**작성일**: 2026-02-08 (수정)
**작성자**: Claude Code (Sonnet 4.5)
**수정 이유**: 신규 구현 방식으로 변경
