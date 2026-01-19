# Database Schema Skill

**PoliticianFinder 데이터베이스 스키마 설계 및 마이그레이션 전문 스킬**

---

## 전문 분야

Supabase (PostgreSQL) 데이터베이스 설계, 마이그레이션, RLS 정책 관리

---

## 핵심 역할

1. **스키마 설계**: ERD 작성 및 테이블 구조 설계
2. **마이그레이션**: SQL 마이그레이션 파일 작성
3. **RLS 정책**: Row Level Security 설정
4. **인덱스 최적화**: 쿼리 성능 개선
5. **데이터 무결성**: Constraints, Triggers 관리

---

## AI-only 원칙 준수

### ✅ 허용
```bash
# CLI로 마이그레이션 실행
supabase db push

# SQL 파일로 스키마 관리
supabase/migrations/20231016_create_politicians.sql

# 로컬 개발
supabase start
supabase db reset
```

### ❌ 금지
- Supabase Dashboard에서 수동 테이블 생성
- SQL Editor에서 직접 실행
- GUI로 RLS 정책 생성

---

## 프로젝트 데이터베이스 구조

### ERD (Entity Relationship Diagram)
```
profiles (사용자 프로필)
  ├── id (PK, FK to auth.users)
  ├── username
  ├── full_name
  ├── role (user/moderator/admin)
  └── created_at

politicians (정치인)
  ├── id (PK)
  ├── name
  ├── party
  ├── region
  ├── position
  ├── bio
  ├── avatar_url
  ├── avg_rating
  └── created_at

ratings (평가)
  ├── id (PK)
  ├── user_id (FK to profiles)
  ├── politician_id (FK to politicians)
  ├── rating (1-5)
  ├── comment
  └── created_at

policies (공약)
  ├── id (PK)
  ├── politician_id (FK to politicians)
  ├── title
  ├── description
  └── status

activities (활동)
  ├── id (PK)
  ├── politician_id (FK to politicians)
  ├── title
  ├── content
  └── date

comments (댓글)
  ├── id (PK)
  ├── user_id (FK to profiles)
  ├── politician_id (FK to politicians)
  ├── parent_id (FK to comments, nullable)
  ├── content
  └── created_at
```

---

## 마이그레이션 파일 작성

### 파일 명명 규칙
```
supabase/migrations/
  ├── 20231016000001_create_profiles.sql
  ├── 20231016000002_create_politicians.sql
  ├── 20231016000003_create_ratings.sql
  └── 20231017000001_add_avg_rating_to_politicians.sql
```

### 1. Profiles 테이블
```sql
-- supabase/migrations/20231016000001_create_profiles.sql

-- Create profiles table
CREATE TABLE IF NOT EXISTS profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  username TEXT UNIQUE NOT NULL,
  full_name TEXT,
  role TEXT NOT NULL DEFAULT 'user' CHECK (role IN ('user', 'moderator', 'admin')),
  avatar_url TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create index
CREATE INDEX idx_profiles_username ON profiles(username);
CREATE INDEX idx_profiles_role ON profiles(role);

-- Enable RLS
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Profiles are viewable by everyone"
  ON profiles FOR SELECT
  USING (true);

CREATE POLICY "Users can update their own profile"
  ON profiles FOR UPDATE
  USING (auth.uid() = id);

-- Create function to handle new user creation
CREATE OR REPLACE FUNCTION handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.profiles (id, username, full_name, avatar_url)
  VALUES (
    NEW.id,
    COALESCE(NEW.raw_user_meta_data->>'username', NEW.email),
    COALESCE(NEW.raw_user_meta_data->>'full_name', ''),
    COALESCE(NEW.raw_user_meta_data->>'avatar_url', '')
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger on auth.users
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION handle_new_user();

-- Comment
COMMENT ON TABLE profiles IS '사용자 프로필 정보';
```

### 2. Politicians 테이블
```sql
-- supabase/migrations/20231016000002_create_politicians.sql

CREATE TABLE IF NOT EXISTS politicians (
  id BIGSERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  party TEXT NOT NULL,
  region TEXT NOT NULL,
  position TEXT NOT NULL,
  bio TEXT,
  avatar_url TEXT,
  avg_rating DECIMAL(3, 2) DEFAULT 0 CHECK (avg_rating >= 0 AND avg_rating <= 5),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_politicians_party ON politicians(party);
CREATE INDEX idx_politicians_region ON politicians(region);
CREATE INDEX idx_politicians_avg_rating ON politicians(avg_rating DESC);
CREATE INDEX idx_politicians_name ON politicians USING gin(to_tsvector('korean', name));

-- Enable RLS
ALTER TABLE politicians ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Politicians are viewable by everyone"
  ON politicians FOR SELECT
  USING (true);

CREATE POLICY "Only admins can insert politicians"
  ON politicians FOR INSERT
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM profiles
      WHERE id = auth.uid() AND role = 'admin'
    )
  );

CREATE POLICY "Only admins can update politicians"
  ON politicians FOR UPDATE
  USING (
    EXISTS (
      SELECT 1 FROM profiles
      WHERE id = auth.uid() AND role = 'admin'
    )
  );

-- Updated at trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_updated_at
  BEFORE UPDATE ON politicians
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

COMMENT ON TABLE politicians IS '정치인 기본 정보';
```

### 3. Ratings 테이블
```sql
-- supabase/migrations/20231016000003_create_ratings.sql

CREATE TABLE IF NOT EXISTS ratings (
  id BIGSERIAL PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  politician_id BIGINT NOT NULL REFERENCES politicians(id) ON DELETE CASCADE,
  rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
  comment TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE(user_id, politician_id)
);

-- Indexes
CREATE INDEX idx_ratings_user_id ON ratings(user_id);
CREATE INDEX idx_ratings_politician_id ON ratings(politician_id);
CREATE INDEX idx_ratings_rating ON ratings(rating);

-- Enable RLS
ALTER TABLE ratings ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Ratings are viewable by everyone"
  ON ratings FOR SELECT
  USING (true);

CREATE POLICY "Users can insert their own ratings"
  ON ratings FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own ratings"
  ON ratings FOR UPDATE
  USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own ratings"
  ON ratings FOR DELETE
  USING (auth.uid() = user_id);

-- Function to update politician avg_rating
CREATE OR REPLACE FUNCTION update_politician_avg_rating()
RETURNS TRIGGER AS $$
BEGIN
  UPDATE politicians
  SET avg_rating = (
    SELECT COALESCE(AVG(rating), 0)
    FROM ratings
    WHERE politician_id = COALESCE(NEW.politician_id, OLD.politician_id)
  )
  WHERE id = COALESCE(NEW.politician_id, OLD.politician_id);
  RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Triggers
CREATE TRIGGER update_avg_rating_on_insert
  AFTER INSERT ON ratings
  FOR EACH ROW EXECUTE FUNCTION update_politician_avg_rating();

CREATE TRIGGER update_avg_rating_on_update
  AFTER UPDATE ON ratings
  FOR EACH ROW EXECUTE FUNCTION update_politician_avg_rating();

CREATE TRIGGER update_avg_rating_on_delete
  AFTER DELETE ON ratings
  FOR EACH ROW EXECUTE FUNCTION update_politician_avg_rating();

COMMENT ON TABLE ratings IS '정치인 평가 및 리뷰';
```

### 4. Comments 테이블
```sql
-- supabase/migrations/20231016000004_create_comments.sql

CREATE TABLE IF NOT EXISTS comments (
  id BIGSERIAL PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  politician_id BIGINT NOT NULL REFERENCES politicians(id) ON DELETE CASCADE,
  parent_id BIGINT REFERENCES comments(id) ON DELETE CASCADE,
  content TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_comments_user_id ON comments(user_id);
CREATE INDEX idx_comments_politician_id ON comments(politician_id);
CREATE INDEX idx_comments_parent_id ON comments(parent_id);
CREATE INDEX idx_comments_created_at ON comments(created_at DESC);

-- Enable RLS
ALTER TABLE comments ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Comments are viewable by everyone"
  ON comments FOR SELECT
  USING (true);

CREATE POLICY "Authenticated users can insert comments"
  ON comments FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own comments"
  ON comments FOR UPDATE
  USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own comments"
  ON comments FOR DELETE
  USING (auth.uid() = user_id);

CREATE TRIGGER set_comments_updated_at
  BEFORE UPDATE ON comments
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

COMMENT ON TABLE comments IS '정치인에 대한 댓글 및 토론';
```

---

## 데이터 시딩

### 개발용 시드 데이터
```sql
-- supabase/seed.sql

-- Insert test politicians
INSERT INTO politicians (name, party, region, position, bio) VALUES
  ('홍길동', '테스트당', '서울 강남구', '국회의원', '테스트 정치인 1'),
  ('김철수', '샘플당', '부산 해운대구', '시의원', '테스트 정치인 2'),
  ('이영희', '예시당', '대구 수성구', '도지사', '테스트 정치인 3');

-- Insert test ratings (requires actual user_ids from auth.users)
-- 이 부분은 실제 사용자가 생성된 후 실행
```

---

## 쿼리 최적화

### 1. 인덱스 추가
```sql
-- 복합 인덱스
CREATE INDEX idx_politicians_party_region ON politicians(party, region);

-- 전문 검색 인덱스 (한글 지원)
CREATE INDEX idx_politicians_search ON politicians USING gin(to_tsvector('korean', name || ' ' || COALESCE(bio, '')));
```

### 2. 성능 분석
```sql
-- 쿼리 실행 계획 확인
EXPLAIN ANALYZE
SELECT * FROM politicians
WHERE party = '테스트당' AND region = '서울';

-- 느린 쿼리 로깅
ALTER DATABASE postgres SET log_min_duration_statement = 1000;
```

---

## RLS 정책 테스트

```sql
-- 현재 사용자 확인
SELECT auth.uid();

-- RLS 정책 테스트 (관리자)
SET request.jwt.claims.sub = 'admin_user_id';
SELECT * FROM politicians;

-- RLS 정책 테스트 (일반 사용자)
SET request.jwt.claims.sub = 'regular_user_id';
INSERT INTO politicians (name, party, region, position)
VALUES ('테스트', '당', '지역', '직책');
-- 실패해야 함
```

---

## 백업 및 복원

```bash
# 스키마 덤프
supabase db dump --schema public > schema.sql

# 데이터 백업
pg_dump -h db.xxx.supabase.co -U postgres -d postgres > backup.sql

# 복원
psql -h db.xxx.supabase.co -U postgres -d postgres < backup.sql
```

---

## 마이그레이션 관리

### 새 마이그레이션 생성
```bash
# CLI로 마이그레이션 파일 생성
supabase migration new add_likes_to_comments
```

### 마이그레이션 적용
```bash
# 로컬 개발
supabase db reset  # 모든 마이그레이션 재적용

# 프로덕션
supabase db push  # 새로운 마이그레이션만 적용
```

### 마이그레이션 롤백
```sql
-- 마이그레이션 롤백용 SQL 작성
-- supabase/migrations/20231016000005_add_likes_rollback.sql

DROP TABLE IF EXISTS likes;
```

---

## 데이터 무결성

### Foreign Key Constraints
```sql
-- ON DELETE CASCADE: 부모 삭제 시 자식도 삭제
-- ON DELETE SET NULL: 부모 삭제 시 자식의 FK를 NULL로
-- ON DELETE RESTRICT: 자식이 있으면 부모 삭제 불가

ALTER TABLE ratings
ADD CONSTRAINT fk_user
FOREIGN KEY (user_id) REFERENCES profiles(id)
ON DELETE CASCADE;
```

### Check Constraints
```sql
ALTER TABLE politicians
ADD CONSTRAINT check_rating_range
CHECK (avg_rating >= 0 AND avg_rating <= 5);
```

---

## 작업 완료 보고 템플릿

```markdown
=== DB 스키마 작업 완료 보고 ===

## 생성 테이블
- profiles: 사용자 프로필
- politicians: 정치인 정보
- ratings: 평가
- comments: 댓글

## 적용된 마이그레이션
- 20231016000001_create_profiles.sql
- 20231016000002_create_politicians.sql
- 20231016000003_create_ratings.sql
- 20231016000004_create_comments.sql

## RLS 정책
- 모든 테이블에 RLS 활성화
- 읽기: 모든 사용자
- 쓰기: 인증된 사용자/관리자

## 인덱스
- 검색 성능 최적화 인덱스 추가
- 전문 검색 인덱스 (한글 지원)

## 테스트 결과
✅ 마이그레이션 적용 성공
✅ RLS 정책 검증 완료
✅ 시드 데이터 삽입 성공

## 다음 단계
- 추가 테이블 (policies, activities) 생성
- 성능 모니터링
- 백업 자동화
```

---

**이 스킬을 사용하면 안전하고 확장 가능한 데이터베이스를 설계하고 관리할 수 있습니다.**
