# 주의사항 (CAUTION)

프로덕션 배포 전 반드시 확인해야 할 사항들

---

## 개발 환경 RLS 정책

**현재 상태:** 개발용 RLS 적용 중 (anon 접근 허용)
- `07_learning_contents_rls_dev.sql`
- `10_faqs_rls_dev.sql`

**프로덕션 배포 전 필수:**
```sql
-- 원래 RLS로 교체
07_learning_contents_rls.sql
10_faqs_rls.sql
```

---

## 본개발 TODO

### 토스페이먼츠
- [ ] 가맹점 등록 (심사 1-2주 소요)
- [ ] 빌링키 발급 API 연동
- [ ] 결제 웹훅 처리

### PG 이용약관
- [ ] 전자금융거래 이용약관 동의 체크박스
- [ ] 개인정보 제3자 제공 동의 체크박스

---

## header.html 자동 admin 로그인 제거 (프로덕션 배포 전 필수!)

**파일:** `Valuation_Company/valuation-platform/frontend/components/header.html`
**위치:** `initAuthState()` 함수 내부 (line 591~600 부근)

**현재 상태 (개발/데모용):**
```javascript
// 관리자 자동 로그인 초기화 (로그아웃 전까지 유지)
if (!localStorage.getItem('loggedOut')) {
    if (!localStorage.getItem('userRole')) {
        localStorage.setItem('userRole', 'admin');
        localStorage.setItem('userEmail', 'wksun999@gmail.com');
        localStorage.setItem('userName', '선웅규');
    }
}
```

**프로덕션 배포 전 필수 조치:**
- [ ] 위 코드 블록 전체 삭제
- [ ] 삭제 후 비로그인 사용자는 로그인/회원가입 버튼만 표시됨
- [ ] 실제 로그인 흐름(login.html)으로만 역할이 설정되도록 보장

**커밋 참조:** `cb36262` (2026-02-03)
