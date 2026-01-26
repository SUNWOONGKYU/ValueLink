# 네이버 검색 API를 활용한 Deal 정보 보강

## 개요

투자 뉴스에서 추출한 기업 정보가 불완전할 때, 네이버 검색 API를 사용하여 자동으로 추가 정보를 수집합니다.

---

## 작동 프로세스

```
[1단계] 투자 뉴스 기사 수집
  └─ Gemini API로 기본 정보 추출
     ├─ 기업명 ✅
     ├─ 업종 ✅
     ├─ 투자금액 ✅
     ├─ CEO: ? ❌
     ├─ 설립일: ? ❌
     └─ 본사 위치: ? ❌

[2단계] 누락 필드 확인
  └─ 없는 필드만 검색 대상으로 선정

[3단계] 네이버 검색 API 호출
  └─ 검색어: "{기업명} 스타트업 대표 설립"
     예: "카카오AI 스타트업 대표 설립"

[4단계] 검색 결과에서 정보 추출
  └─ 정규식 패턴 매칭으로 자동 추출
     ├─ "대표 김철수" → CEO: 김철수
     ├─ "2023년 설립" → Founded: 2023-01-01
     └─ "본사 서울" → Location: 서울

[5단계] 기존 정보에 병합
  └─ 기존 값이 있으면 유지 (덮어쓰기 안 함)
     기존 값이 없으면 검색 결과로 추가

[6단계] 완성된 정보로 Deal 저장
```

---

## API 키 발급 방법

### 1. 네이버 개발자 센터 접속
- https://developers.naver.com/
- 로그인

### 2. 애플리케이션 등록
- 상단 메뉴: Application → 애플리케이션 등록
- 애플리케이션 이름: `투자뉴스수집기` (원하는 이름)
- 사용 API: **검색** ✅ 체크
- 웹 서비스 URL: `http://localhost`

### 3. API 키 확인
- Client ID: `aBcDeFgHiJkL1234` (예시)
- Client Secret: `XyZ9876543210` (예시)

### 4. .env 파일에 추가
```bash
NAVER_CLIENT_ID=aBcDeFgHiJkL1234
NAVER_CLIENT_SECRET=XyZ9876543210
```

---

## 검색 로직 상세

### 검색 쿼리 생성
```python
company_name = "카카오AI"
search_query = f"{company_name} 스타트업 대표 설립"
```

### API 호출
```python
url = "https://openapi.naver.com/v1/search/blog.json"
headers = {
    'X-Naver-Client-Id': NAVER_CLIENT_ID,
    'X-Naver-Client-Secret': NAVER_CLIENT_SECRET
}
params = {
    'query': search_query,
    'display': 10,  # 10개 결과
    'sort': 'sim'   # 정확도순
}
response = requests.get(url, headers=headers, params=params)
```

### 정규식 패턴

#### CEO 추출
```python
patterns = [
    r'대표[:\s]+([가-힣]{2,4})',     # "대표 김철수"
    r'CEO[:\s]+([가-힣]{2,4})',      # "CEO 김철수"
    r'대표이사[:\s]+([가-힣]{2,4})'  # "대표이사 김철수"
]
```

#### 설립일 추출
```python
patterns = [
    r'(\d{4})년\s*설립',  # "2023년 설립"
    r'설립[:\s]+(\d{4})'  # "설립 2023"
]
```

#### 본사 위치 추출
```python
location_keywords = ['서울', '경기', '판교', '강남', '부산', '대전']
# 키워드 존재 여부 확인
```

---

## 효과

### Before (네이버 API 없음)
```
22개 Deal 저장
- CEO: 22.7% (5/22)
- Founded: 9.1% (2/22)
- Location: 13.6% (3/22)
```

### After (네이버 API 사용)
```
예상:
- CEO: 50%+
- Founded: 40%+
- Location: 50%+
```

---

## 비용 및 제한

### 무료 플랜
- **하루 25,000회** 호출 가능
- **초당 10회** 제한
- 우리 사용량: 하루 약 **100회** (충분!)

### Rate Limiting 처리
```python
time.sleep(0.1)  # 초당 10회 제한 준수
```

---

## 백업: 구글 검색

네이버 API 키가 없거나 오류 시, 자동으로 구글 검색으로 백업:

```python
if not NAVER_CLIENT_ID:
    print("[WARNING] Naver API keys not found")
    print("[INFO] Trying Google search...")
    result = search_company_info_google(company_name)
```

---

## 관련 파일

| 파일 | 설명 |
|------|------|
| `search_company_info.py` | 검색 기능 구현 |
| `select_and_move_to_deals.py` | 메인 스크립트 (검색 호출) |
| `.env` | API 키 저장 |

---

## 예시: 카카오AI

### 검색 전
```json
{
  "company_name": "카카오AI",
  "industry": "AI",
  "ceo": null,
  "founded": null,
  "location": null
}
```

### 네이버 검색 실행
```
검색어: "카카오AI 스타트업 대표 설립"

검색 결과:
1. "카카오AI는 2023년 설립된 AI 스타트업..."
2. "CEO 김성훈이 이끄는 카카오AI..."
3. "일본 도쿄에 본사를 둔 카카오AI..."
```

### 정보 추출
```
- CEO: "김성훈" (패턴 매칭 성공)
- Founded: "2023-01-01" (2023년 추출)
- Location: "일본" (키워드 발견)
```

### 검색 후
```json
{
  "company_name": "카카오AI",
  "industry": "AI",
  "ceo": "김성훈",        ← 추가됨!
  "founded": "2023-01-01", ← 추가됨!
  "location": "일본"       ← 추가됨!
}
```

---

## 문제 해결

### API 키 오류
```
Error: Invalid Client ID or Secret
→ .env 파일의 API 키 확인
→ 네이버 개발자 센터에서 재발급
```

### 정보 추출 실패
```
검색 결과는 나오지만 정보 추출 안 됨
→ 정규식 패턴 개선 필요
→ 검색어 키워드 조정
```

### Rate Limit 초과
```
429 Too Many Requests
→ time.sleep() 시간 증가
→ 하루 25,000회 제한 확인
```

---

## 향후 개선 방향

1. **정규식 패턴 추가**
   - 영문 CEO 이름 지원
   - 더 다양한 날짜 형식

2. **검색어 최적화**
   - 기업명 + 업종 조합
   - 투자 정보 포함

3. **추가 API 연동**
   - 기업데이터 API
   - 공공데이터 포털

---

## 참고 링크

- [네이버 개발자 센터](https://developers.naver.com/)
- [네이버 검색 API 가이드](https://developers.naver.com/docs/serviceapi/search/blog/blog.md)
- [API 사용량 확인](https://developers.naver.com/apps/)
