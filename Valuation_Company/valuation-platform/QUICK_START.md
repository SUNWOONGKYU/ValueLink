# 🚀 빠른 시작 가이드

**5분 안에 기업가치평가 플랫폼 확인하기**

---

## 1️⃣ 웹 서버 실행 (30초)

### Windows (명령 프롬프트)
```bash
cd C:\ValueLink\Valuation_Company\valuation-platform\frontend
python -m http.server 3000
```

### 성공 메시지
```
Serving HTTP on :: port 3000 (http://[::]:3000/) ...
```

**✅ 이 창은 열어둔 채로 다음 단계로!**

---

## 2️⃣ 브라우저에서 열기 (10초)

주소창에 입력:
```
http://localhost:3000/app/valuation-list.html
```

또는 파일 직접 열기:
```
C:\ValueLink\Valuation_Company\valuation-platform\frontend\app\valuation-list.html
```

---

## 3️⃣ 확인할 것들 (2분)

### ✅ 화면에 보여야 할 것들

1. **헤더** - ValueLink 로고, Valuation/Deal 메뉴
2. **필터 버튼** - 전체, DCF, 상대가치, 본질가치, 자산가치, 상증세법
3. **프로젝트 카드 25개** - 깔끔한 카드 형태
4. **통계** - "총 25건" 표시

### ✅ 테스트해보기

| 액션 | 기대 결과 |
|------|----------|
| 페이지 로드 | 25개 카드 표시 |
| "DCF평가법" 클릭 | 5개 카드만 표시 |
| "상대가치평가법" 클릭 | 5개 카드만 표시 |
| "전체" 클릭 | 다시 25개 표시 |
| 카드에 마우스 올리기 | 파란 테두리 + 그림자 |

### ✅ 실제 사례 찾기

**녹색 테두리** + **"실제 사례" 배지**가 있는 5개 카드:

1. **엔키노에이아이** - DCF평가법, 2,140원
2. **삼성전자** - 상대가치평가법, 97,700원
3. **카카오** - 본질가치평가법, 113,429원
4. **클래시스** - 자산가치평가법, 52,774원
5. **비상장법인(조심2022중6580)** - 상증세법평가법, 110,000원

---

## 4️⃣ 문제 발생 시 (1분)

### Q1: 서버가 안 켜져요
```bash
# Python 설치 확인
python --version

# 또는 Python 3 사용
python3 -m http.server 3000
```

### Q2: 데이터가 안 보여요

브라우저 **개발자 도구** 열기 (F12):
- **Console** 탭 → 에러 메시지 확인
- **Network** 탭 → Supabase 요청 확인

Supabase 데이터 확인:
```bash
cd C:\ValueLink\Valuation_Company\valuation-platform\backend
python check_data.py
```

### Q3: 필터가 작동 안 해요

- 브라우저 새로고침 (Ctrl+R)
- 캐시 삭제 후 새로고침 (Ctrl+Shift+R)

---

## 5️⃣ 다음 단계

### 즉시 해볼 수 있는 것들

1. **카드 클릭**
   - 콘솔(F12)에 상세 정보 출력됨
   - 추후 모달로 확장 예정

2. **모바일 뷰 확인**
   - 브라우저 크기 조절
   - 반응형 디자인 확인

3. **API 테스트 페이지**
   ```
   http://localhost:3000/app/test-api.html
   ```
   - "전체 테스트 실행" 버튼 클릭
   - 8개 테스트 모두 PASS 확인

---

## 📊 데이터 확인

### Backend 테스트 실행
```bash
cd C:\ValueLink\Valuation_Company\valuation-platform\backend
python test_api_integration.py
```

**기대 결과:**
```
Passed: 8/8 (100.0%)
```

---

## 📁 파일 구조

```
valuation-platform/
├── frontend/
│   └── app/
│       ├── valuation-list.html    ← 메인 페이지
│       └── test-api.html          ← 테스트 페이지
├── backend/
│   ├── create_tables.sql
│   ├── insert_realistic_data.py
│   ├── check_data.py
│   └── test_api_integration.py
├── TEST_REPORT.md                 ← 상세 테스트 결과
├── FINAL_SUMMARY.md               ← 전체 요약
└── QUICK_START.md                 ← 이 파일
```

---

## 🎯 체크리스트

확인했으면 체크하세요!

- [ ] 웹 서버 실행 성공
- [ ] 프로젝트 목록 페이지 로드됨
- [ ] 25개 카드가 보임
- [ ] 필터 버튼 작동함
- [ ] 실제 사례 5개 구분됨 (녹색 테두리)
- [ ] 카드 호버 효과 작동
- [ ] API 테스트 페이지도 확인함

**모두 체크했다면 성공! 🎉**

---

## 💬 다음 작업 제안

1. **상세 정보 모달 추가** - 카드 클릭 시 팝업
2. **검색 기능** - 기업명으로 검색
3. **차트 추가** - 평가법별 분포 차트
4. **프로젝트 생성** - 새 평가 요청 폼

어떤 것부터 시작할까요?

---

**즐거운 하루 되세요! ☕️**
