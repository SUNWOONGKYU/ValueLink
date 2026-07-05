# 해결책: REST API 직접 사용

**작성일**: 2026-01-25
**문제**: supabase-py 라이브러리가 테이블을 못 찾음
**해결**: REST API를 직접 사용

---

## ✅ 확인된 사실

1. ✅ Supabase 테이블 정상 생성
2. ✅ REST API 정상 작동 (curl로 INSERT 성공)
3. ❌ Python supabase-py 라이브러리 오류

---

## 🔧 해결 방법: requests 라이브러리로 REST API 직접 호출

### 수정할 함수: `save_to_supabase()`

**파일**: `scrape_investment_news.py`

**기존 코드** (라인 377-403):
```python
def save_to_supabase(articles: List[Dict]) -> int:
    if not articles:
        return 0

    saved_count = 0
    batch_size = 100

    for i in range(0, len(articles), batch_size):
        batch = articles[i:i + batch_size]

        try:
            response = supabase.table('investment_news_articles').insert(batch).execute()
            saved_count += len(batch)
            logger.info(f"💾 Supabase 저장: {len(batch)}건 (누적: {saved_count}건)")
        except Exception as e:
            if 'duplicate' in str(e).lower() or 'unique' in str(e).lower():
                logger.warning(f"⚠️  중복 URL 감지, 스킵: {len(batch)}건")
            else:
                logger.error(f"❌ Supabase 저장 실패: {e}")

    return saved_count
```

**새 코드** (REST API 직접 사용):
```python
def save_to_supabase(articles: List[Dict]) -> int:
    """
    수집된 기사를 Supabase에 저장 (REST API 직접 호출)
    """
    if not articles:
        return 0

    saved_count = 0
    batch_size = 100

    # REST API 엔드포인트
    api_url = f"{SUPABASE_URL}/rest/v1/investment_news_articles"
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json',
        'Prefer': 'return=representation'
    }

    for i in range(0, len(articles), batch_size):
        batch = articles[i:i + batch_size]

        try:
            # REST API POST 요청
            response = requests.post(api_url, json=batch, headers=headers, timeout=30)

            if response.status_code == 201:
                saved_count += len(batch)
                logger.info(f"💾 Supabase 저장: {len(batch)}건 (누적: {saved_count}건)")
            elif response.status_code == 409:
                # 중복 URL
                logger.warning(f"⚠️  중복 URL 감지, 스킵: {len(batch)}건")
            else:
                logger.error(f"❌ Supabase 저장 실패 (HTTP {response.status_code}): {response.text}")

        except requests.RequestException as e:
            logger.error(f"❌ Supabase 저장 요청 실패: {e}")
        except Exception as e:
            logger.error(f"❌ Supabase 저장 오류: {e}")

    return saved_count
```

---

## 📝 전체 수정 단계

### 1. import 문 확인

파일 상단에 `requests`가 이미 import되어 있는지 확인 (라인 14):
```python
import requests  # 이미 있음
```

### 2. supabase 클라이언트 제거 (선택 사항)

더 이상 필요 없으므로 제거 가능 (라인 17, 45):
```python
# from supabase import create_client, Client  # 주석 처리
# supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)  # 주석 처리
```

### 3. `save_to_supabase()` 함수 교체

위의 새 코드로 교체

### 4. 테스트

```bash
python scrape_investment_news.py
```

---

## ✅ 예상 결과

- ✅ Supabase 저장 성공
- ✅ "💾 Supabase 저장: N건" 메시지 출력
- ✅ Supabase 테이블에 데이터 축적

---

## 🔍 검증 방법

### Supabase에서 확인:
```sql
SELECT COUNT(*) FROM investment_news_articles;
SELECT site_name, COUNT(*) FROM investment_news_articles GROUP BY site_name;
```

### curl로 확인:
```bash
curl -X GET "https://arxrfetgaitkgiiqabap.supabase.co/rest/v1/investment_news_articles?select=count" \
  -H "apikey: [YOUR_KEY]" \
  -H "Authorization: Bearer [YOUR_KEY]" \
  -H "Prefer: count=exact"
```

---

## 📌 참고

- REST API 문서: https://supabase.com/docs/guides/api
- HTTP 상태 코드:
  - 201: 생성 성공
  - 409: 중복 (UNIQUE 제약 위반)
  - 400: 잘못된 요청
  - 401: 인증 실패
