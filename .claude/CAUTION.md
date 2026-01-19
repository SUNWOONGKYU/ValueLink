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
