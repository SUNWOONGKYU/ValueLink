# Phase 1: 데이터베이스 스키마 구축 가이드

> 내부 사용자 3개 (Customer, Accountant, Admin) 역할 기반 시스템 구축

---

## 📋 실행 파일 목록

| 순서 | 파일 | 설명 | 필수 여부 |
|------|------|------|----------|
| 1 | `create_users_table.sql` | 사용자 역할 관리 테이블 생성 | ✅ 필수 |
| 2 | `create_accountants_table.sql` | 공인회계사 프로필 테이블 생성 | ✅ 필수 |
| 3 | `alter_customers_table.sql` | 고객사 테이블 수정 | ✅ 필수 |
| 4 | `alter_projects_table.sql` | 프로젝트 테이블 수정 | ✅ 필수 |

---

## 🚀 실행 순서 (중요!)

### ⚠️ 반드시 순서대로 실행해야 합니다!

```
1. create_users_table.sql         (users 테이블 생성)
    ↓
2. create_accountants_table.sql   (accountants 테이블 생성, users 참조)
    ↓
3. alter_customers_table.sql      (customers에 user_id 추가)
    ↓
4. alter_projects_table.sql       (projects에 assigned_accountant_id 추가)
```

**이유**: 외래키 참조 관계 때문에 순서가 중요합니다.
- `accountants.user_id` → `users.user_id` 참조
- `customers.user_id` → `users.user_id` 참조
- `projects.assigned_accountant_id` → `accountants.accountant_id` 참조

---

## 📝 실행 방법

### 방법 1: Supabase Dashboard (권장)

1. **Supabase Dashboard 접속**
   ```
   https://supabase.com/dashboard
   ```

2. **프로젝트 선택**
   - ValueLink 프로젝트 클릭

3. **SQL Editor 열기**
   - 왼쪽 메뉴 → "SQL Editor" 클릭

4. **파일 내용 복사 & 실행**
   - 순서 1: `create_users_table.sql` 내용 복사 → 붙여넣기 → "Run" 클릭
   - 순서 2: `create_accountants_table.sql` 내용 복사 → 붙여넣기 → "Run" 클릭
   - 순서 3: `alter_customers_table.sql` 내용 복사 → 붙여넣기 → "Run" 클릭
   - 순서 4: `alter_projects_table.sql` 내용 복사 → 붙여넣기 → "Run" 클릭

5. **실행 결과 확인**
   - 각 쿼리 실행 후 "Success" 메시지 확인
   - 에러 발생 시 메시지 확인 후 수정

### 방법 2: Supabase CLI (선택사항)

```bash
# 순서대로 실행
supabase db reset
supabase db push create_users_table.sql
supabase db push create_accountants_table.sql
supabase db push alter_customers_table.sql
supabase db push alter_projects_table.sql
```

---

## ✅ 실행 확인

### 테이블 생성 확인

Supabase Dashboard → Table Editor에서 다음 테이블 확인:

- ✅ `users` (신규)
- ✅ `accountants` (신규)
- ✅ `customers` (수정됨)
- ✅ `projects` (수정됨)

### 필드 확인

#### users 테이블
```sql
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'users';
```

예상 결과:
- user_id (uuid)
- email (character varying)
- role (character varying)
- name (character varying)
- phone (character varying)
- is_active (boolean)

#### accountants 테이블
```sql
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'accountants';
```

예상 결과:
- accountant_id (character varying)
- user_id (uuid)
- license_number (character varying)
- education (ARRAY)
- career (ARRAY)
- specialization (ARRAY)
- rating (numeric)

#### customers 테이블 (추가 필드 확인)
```sql
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'customers'
AND column_name IN ('user_id', 'company_name_en');
```

예상 결과:
- user_id (uuid)
- company_name_en (character varying)

#### projects 테이블 (추가 필드 확인)
```sql
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'projects'
AND column_name IN ('assigned_accountant_id', 'company_name_kr', 'budget');
```

예상 결과:
- assigned_accountant_id (character varying)
- company_name_kr (character varying)
- company_name_en (character varying)
- budget (character varying)

---

## 🔧 문제 해결

### 에러 1: "relation does not exist"
**원인**: 테이블 실행 순서가 잘못됨
**해결**: 순서대로 다시 실행 (1 → 2 → 3 → 4)

### 에러 2: "column already exists"
**원인**: 이미 실행한 적이 있음
**해결**: `IF NOT EXISTS` 구문 때문에 무시해도 됨 (정상)

### 에러 3: "foreign key constraint"
**원인**: 참조 테이블이 아직 생성되지 않음
**해결**: 순서 1번 (users)부터 다시 실행

### 에러 4: "permission denied"
**원인**: Supabase 권한 문제
**해결**: Supabase Dashboard에서 관리자 계정으로 로그인 확인

---

## 🧪 테스트 데이터

### 샘플 사용자 생성

```sql
-- 1. 고객 사용자 생성
INSERT INTO users (user_id, email, role, name, phone, is_active)
VALUES (
    gen_random_uuid(),
    'customer1@test.com',
    'customer',
    '김철수',
    '010-1234-5678',
    true
);

-- 2. 공인회계사 사용자 생성
INSERT INTO users (user_id, email, role, name, phone, is_active)
VALUES (
    gen_random_uuid(),
    'accountant1@test.com',
    'accountant',
    '박영희',
    '010-2345-6789',
    true
);

-- 3. 관리자 사용자 생성
INSERT INTO users (user_id, email, role, name, phone, is_active)
VALUES (
    gen_random_uuid(),
    'admin@valuelink.com',
    'admin',
    '관리자',
    '010-0000-0000',
    true
);
```

### 샘플 공인회계사 프로필 생성

```sql
-- 공인회계사 프로필 생성
INSERT INTO accountants (
    accountant_id,
    user_id,
    license_number,
    education,
    career,
    specialization,
    bio,
    rating,
    is_available
)
VALUES (
    generate_accountant_id(),  -- 자동 생성 함수
    (SELECT user_id FROM users WHERE email = 'accountant1@test.com'),
    'CPA-2020-12345',
    ARRAY['서울대학교 경영학과 학사', '연세대학교 회계학 석사'],
    ARRAY['삼일회계법인 5년', '삼정KPMG 3년', '독립 공인회계사 2년'],
    ARRAY['DCF', '상대가치', '본질가치'],
    '10년 경력의 기업가치 평가 전문가입니다.',
    4.8,
    true
);
```

---

## 📌 다음 단계

Phase 1 완료 후:

✅ **Phase 2: 마이페이지 구축**
- mypage.html (라우터)
- mypage-customer.html
- mypage-accountant.html
- mypage-admin.html

진행 방법:
```bash
# Phase 1 완료 확인
# → Phase 2 시작
```

---

## 📞 문의

문제가 발생하면:
1. 에러 메시지 전체 복사
2. 실행한 SQL 파일명 확인
3. 이전 단계 실행 여부 확인

---

## 📚 참고

- [Supabase 공식 문서](https://supabase.com/docs)
- [PostgreSQL 외래키 문서](https://www.postgresql.org/docs/current/ddl-constraints.html)
- [RLS (Row Level Security) 가이드](https://supabase.com/docs/guides/auth/row-level-security)
