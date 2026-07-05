# 스크래핑 이슈 수정 가이드

**작성일**: 2026-01-25
**대상**: 재미나 ICI

---

## 🔴 발견된 문제

### 1. 테이블 없음 오류
**오류 메시지**: `investment_news_articles` 테이블을 찾을 수 없음

**원인**: 사용자가 `create_tables.sql`을 Supabase에서 실행하지 않았을 가능성

**해결 방법**:
1. 사용자에게 확인 요청
2. Supabase SQL Editor에서 다음 쿼리 실행:
   ```sql
   SELECT table_name
   FROM information_schema.tables
   WHERE table_schema = 'public'
   AND table_name IN ('investment_news_articles', 'investment_news_ranking');
   ```
3. 테이블이 없으면 `create_tables.sql` 전체를 Supabase에서 실행

---

### 2. SSL 오류 - 벤처경영신문 (사이트 20)

**오류 메시지**:
```
HTTPSConnectionPool(host='www.vmnews.co.kr', port=443):
Max retries exceeded with url: / (Caused by SSLError)
```

**해결 방법**: `scrape_site_dispatch` 함수 수정

**수정 위치**: `scrape_investment_news.py` 라인 331-370

**수정 코드**:
```python
def scrape_site_dispatch(site: Dict) -> List[Dict]:
    articles = []
    site_number = site['number']
    site_name = site['name']
    site_url = site['url']

    logger.info(f"🔍 [{site_number}] {site_name} 스크래핑 시작...")

    try:
        # SSL 검증 비활성화가 필요한 사이트
        verify_ssl = True
        if site_number == 20:  # 벤처경영신문
            verify_ssl = False
            logger.warning(f"⚠️ [{site_number}] {site_name}: SSL 검증 비활성화")

        # 사이트 메인 페이지 요청
        response = requests.get(site_url, headers=HEADERS, timeout=10, verify=verify_ssl)
        response.raise_for_status()
        response.encoding = 'utf-8'

        soup = BeautifulSoup(response.text, 'lxml')

        # 해당 사이트에 맞는 스크래퍼 함수 호출
        scraper_func = SITE_SCRAPERS.get(site_url)
        if scraper_func:
            articles = scraper_func(soup, site)
        else:
            logger.error(f"❌ [{site_number}] {site_name}에 대한 스크래퍼 함수를 찾을 수 없습니다.")

        logger.info(f"✅ [{site_number}] {site_name}: {len(articles)}건 수집")

    except requests.RequestException as e:
        logger.error(f"❌ [{site_number}] {site_name} 요청 실패: {e}")
    except Exception as e:
        logger.error(f"❌ [{site_number}] {site_name} 스크래핑 오류: {e}")

    return articles
```

**변경 사항**:
- `verify_ssl` 변수 추가
- 사이트 20번(벤처경영신문)일 때 `verify=False` 설정
- `requests.get()`에 `verify=verify_ssl` 파라미터 추가

---

### 3. 404 오류 - 다음뉴스 (사이트 25)

**오류 메시지**:
```
404 Client Error: Not Found for url: https://news.daum.net/section/2/venture
```

**원인**: URL이 변경되었거나 존재하지 않음

**해결 방법 1**: URL 수정

다음뉴스의 실제 벤처/스타트업 섹션 URL 확인 필요:
- 옵션 A: `https://news.daum.net/breakingnews/economic/venture`
- 옵션 B: `https://news.daum.net/economic#venture`
- 옵션 C: 검색 URL 사용

**수정 위치**: `scrape_investment_news.py` 라인 66

**Before**:
```python
{'number': 25, 'name': '다음뉴스 벤처/스타트업', 'url': 'https://news.daum.net/section/2/venture'},
```

**After** (옵션 A):
```python
{'number': 25, 'name': '다음뉴스 벤처/스타트업', 'url': 'https://news.daum.net/breakingnews/economic/venture'},
```

**해결 방법 2**: 브라우저로 확인

1. https://news.daum.net 접속
2. "경제" 또는 "IT/과학" 섹션 확인
3. "벤처" 또는 "스타트업" 카테고리 찾기
4. 실제 URL 확인 후 수정

**해결 방법 3**: 다음 검색 사용

```python
{'number': 25, 'name': '다음뉴스 벤처/스타트업', 'url': 'https://search.daum.net/search?w=news&q=투자유치'},
```

---

## 📋 수정 체크리스트

### 사용자 확인 사항
- [ ] Supabase에서 테이블 존재 확인
- [ ] 테이블 없으면 `create_tables.sql` 실행
- [ ] 테이블 생성 확인 쿼리 실행

### 재미나 ICI 수정 사항
- [ ] `scrape_site_dispatch` 함수에 SSL 검증 비활성화 로직 추가
- [ ] 다음뉴스 URL 확인 및 수정
- [ ] 수정된 스크립트 테스트
- [ ] 재실행하여 데이터 수집 확인

---

## 🚀 수정 후 실행 순서

1. **사용자**: Supabase 테이블 확인 및 생성
2. **재미나 ICI**: 스크립트 수정
3. **재미나 ICI**: 스크립트 재실행
   ```bash
   python scrape_investment_news.py
   ```
4. **확인**: Supabase에서 데이터 수집 여부 확인
   ```sql
   SELECT COUNT(*) FROM investment_news_articles;
   SELECT site_name, COUNT(*) FROM investment_news_articles GROUP BY site_name;
   ```

---

## 📞 추가 지원

수정 후에도 문제가 발생하면:
- 로그 파일 확인: `scraping_log.txt`
- 특정 사이트 에러 메시지 공유
- 브라우저에서 해당 사이트 접속 가능 여부 확인
