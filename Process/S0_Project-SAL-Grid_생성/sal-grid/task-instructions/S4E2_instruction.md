# S4E2: News Parser & Data Extraction

## Task 정보

- **Task ID**: S4E2
- **Task Name**: 뉴스 파서 및 데이터 추출
- **Stage**: S4 (External Integration - 개발 3차)
- **Area**: E (External)
- **Dependencies**: S4E1 (Base Crawler)
- **Task Agent**: backend-developer
- **Verification Agent**: code-reviewer

---

## Task 목표

HTML에서 투자 뉴스 데이터를 추출하고 Deal 정보를 파싱하는 파서 구현

---

## 상세 지시사항

### 1. 뉴스 파서

**파일**: `lib/crawler/news-parser.ts`

```typescript
import * as cheerio from 'cheerio'

export interface ParsedDealInfo {
  company_name: string              // 기업명
  investment_stage?: string         // 투자 단계 (시드, 시리즈A 등)
  investment_amount?: string        // 투자 금액
  investors: string[]               // 투자자 목록
  industry?: string                 // 업종
  location?: string                 // 지역
}

export interface ParsedArticle {
  title: string
  content: string
  published_date: string
  deal_info?: ParsedDealInfo
}

export class NewsParser {
  /**
   * HTML에서 기사 파싱
   */
  parseArticle(
    html: string,
    selectors: {
      title: string
      content: string
      date: string
    }
  ): ParsedArticle {
    const $ = cheerio.load(html)

    const title = $(selectors.title).text().trim()
    const content = $(selectors.content).text().trim()
    const dateText = $(selectors.date).text().trim()

    const published_date = this.parseDate(dateText)

    // Deal 정보 추출
    const deal_info = this.extractDealInfo(title + ' ' + content)

    return {
      title,
      content,
      published_date,
      deal_info,
    }
  }

  /**
   * Deal 정보 추출 (투자 관련 정보)
   */
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

  /**
   * 기업명 추출
   */
  private extractCompanyName(text: string): string | null {
    // 패턴: "스타트업 XXX", "XXX는", "XXX가"
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

  /**
   * 투자 단계 추출
   */
  private extractInvestmentStage(text: string): string | undefined {
    const stages = [
      '시드',
      '프리A',
      '프리시리즈A',
      '시리즈A',
      '시리즈B',
      '시리즈C',
      '시리즈D',
      '시리즈E',
      '브릿지',
      'Series A',
      'Series B',
      'Series C',
    ]

    for (const stage of stages) {
      if (text.includes(stage)) {
        // 정규화
        return stage
          .replace('프리시리즈A', '프리A')
          .replace('Series A', '시리즈A')
          .replace('Series B', '시리즈B')
          .replace('Series C', '시리즈C')
      }
    }

    return undefined
  }

  /**
   * 투자 금액 추출
   */
  private extractInvestmentAmount(text: string): string | undefined {
    // 패턴: "100억원", "50억 규모", "$10M"
    const patterns = [
      /(\d+(?:,\d+)?억\s*원?)/,
      /(\d+(?:,\d+)?억\s*규모)/,
      /(\$\d+(?:\.\d+)?M)/,
      /(\d+(?:,\d+)?만\s*달러)/,
    ]

    for (const pattern of patterns) {
      const match = text.match(pattern)
      if (match && match[1]) {
        return match[1].replace(/\s+/g, ' ').trim()
      }
    }

    return undefined
  }

  /**
   * 투자자 추출
   */
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

  /**
   * 업종 추출
   */
  private extractIndustry(text: string): string | undefined {
    const industries = [
      'AI',
      '인공지능',
      '헬스케어',
      '의료',
      '핀테크',
      '금융',
      '이커머스',
      '커머스',
      '푸드테크',
      '식품',
      '모빌리티',
      '교육',
      '에듀테크',
      '물류',
      '제조',
      '반도체',
      '바이오',
    ]

    for (const industry of industries) {
      if (text.includes(industry)) {
        // 정규화
        if (industry === '인공지능') return 'AI'
        if (industry === '의료') return '헬스케어'
        if (industry === '금융') return '핀테크'
        if (industry === '커머스') return '이커머스'
        if (industry === '식품') return '푸드테크'
        return industry
      }
    }

    return undefined
  }

  /**
   * 지역 추출
   */
  private extractLocation(text: string): string | undefined {
    const locations = [
      '판교',
      '강남',
      '서울',
      '부산',
      '대구',
      '인천',
      '광주',
      '대전',
      '울산',
      '세종',
    ]

    for (const location of locations) {
      if (text.includes(location)) {
        return location
      }
    }

    return undefined
  }

  /**
   * 날짜 파싱
   */
  private parseDate(dateText: string): string {
    // "2026.02.05", "2026-02-05", "2월 5일" 등 다양한 형식 지원

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

  /**
   * 여러 기사 일괄 파싱
   */
  parseArticles(
    htmlList: Array<{ html: string; url: string }>,
    selectors: {
      title: string
      content: string
      date: string
    }
  ): ParsedArticle[] {
    return htmlList.map(({ html }) => this.parseArticle(html, selectors))
  }
}

// 싱글톤 인스턴스
export const newsParser = new NewsParser()
```

---

## 생성/수정 파일

| 파일 | 변경 내용 | 라인 수 (예상) |
|------|----------|---------------|
| `lib/crawler/news-parser.ts` | 뉴스 파서 | ~300줄 |

**총 파일 수**: 1개
**총 라인 수**: ~300줄

---

## 기술 스택

- **Cheerio**: HTML 파싱 (jQuery-like API)
- **정규표현식**: 텍스트 추출
- **TypeScript 5.x**: 타입 안전성

---

## 완료 기준

### 필수 (Must Have)

- [ ] 기사 파싱 함수 구현 (`parseArticle`)
- [ ] Deal 정보 추출 (`extractDealInfo`)
- [ ] 기업명 추출
- [ ] 투자 단계 추출
- [ ] 투자 금액 추출
- [ ] 투자자 추출
- [ ] 업종 추출
- [ ] 날짜 파싱

### 검증 (Verification)

- [ ] TypeScript 빌드 성공
- [ ] Cheerio HTML 파싱 동작 확인
- [ ] 정규표현식 패턴 테스트
- [ ] 다양한 날짜 형식 파싱 확인

### 권장 (Nice to Have)

- [ ] AI 기반 정보 추출 (Claude API)
- [ ] 추출 정확도 개선
- [ ] 지역 추출 확장

---

## 참조

### 기존 프로토타입
- `backend/app/services/news_parser.py`

### 의존성
- S4E1: Base Crawler

---

## 주의사항

1. **정규표현식 패턴**
   - 다양한 형식 지원
   - 한글/영문 혼용 처리

2. **투자자 추출**
   - 유명 VC 리스트 활용
   - 패턴 매칭 보완

3. **날짜 파싱**
   - 다양한 날짜 형식 지원
   - 파싱 실패 시 현재 날짜

4. **일반 명사 제외**
   - 기업명 추출 시 "투자", "금액" 등 제외

5. **정규화**
   - "인공지능" → "AI"
   - "Series A" → "시리즈A"

---

**작업 복잡도**: Medium
**작성일**: 2026-02-06
**작성자**: Claude Code (Sonnet 4.5)
