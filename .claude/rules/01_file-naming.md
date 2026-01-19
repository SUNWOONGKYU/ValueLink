# 01. 파일명 규칙

> 적용 대상: Production에 저장되는 5개 Area (F, BA, S, BI, E)

---

## 1. 기본 형식

**kebab-case 사용 (소문자 + 하이픈)**

```
✅ 올바른 형식:
- google-login.js
- subscription-cancel.js
- forgot-password.html
- ai-health.js

❌ 잘못된 형식:
- googleLogin.js        (camelCase 금지)
- google_login.js       (snake_case 금지)
- GoogleLogin.js        (PascalCase 금지)
- GOOGLE-LOGIN.js       (대문자 금지)
```

---

## 2. 파일명 구성

**[기능]-[동작].확장자**

| 구성 | 설명 | 예시 |
|------|------|------|
| 기능 | 무엇에 관한 것인지 | google, email, subscription |
| 동작 | 무엇을 하는지 | login, send, cancel |
| 확장자 | 파일 유형 | .js, .html, .css |

```
예시:
- google-login.js       → 기능: google, 동작: login
- email-send.js         → 기능: email, 동작: send
- subscription-cancel.js → 기능: subscription, 동작: cancel
- password-reset.html   → 기능: password, 동작: reset
```

---

## 3. Area별 확장자

| Area | 파일 유형 | 확장자 | 예시 |
|------|----------|--------|------|
| F (Frontend) | 페이지 | `.html` | `google-login.html` |
| F (Frontend) | 스크립트 | `.js` | `sidebar.js` |
| F (Frontend) | 스타일 | `.css` | `dashboard.css` |
| BA (Backend APIs) | API | `.js` | `subscription-cancel.js` |
| S (Security) | 인증 API | `.js` | `google-callback.js` |
| BI (Backend Infra) | 라이브러리 | `.js` | `supabase-client.js` |
| E (External) | 외부 연동 | `.js` | `ai-health.js` |

---

## 4. Task ID 반영 방법

**파일명에는 Task ID 안 넣음 → 파일 상단 주석에 넣음**

```
❌ 파일명에 Task ID 넣지 않음:
- S2BA1_subscription-cancel.js  (X)

✅ 파일명은 기능만, Task ID는 주석에:
- subscription-cancel.js        (O)
```

**JavaScript 파일:**
```javascript
/**
 * @task S2BA1
 * @description 구독 취소 API
 */
export default async function handler(req, res) {
  // ...
}
```

**HTML 파일:**
```html
<!--
@task S2F1
@description Google 로그인 페이지
-->
<!DOCTYPE html>
<html>
...
```

---

## 5. 예외: Non-Production 파일

**Production에 안 들어가는 Area는 자체 규칙 적용**

| Area | 파일명 규칙 | 예시 |
|------|-------------|------|
| D (Database) | `[TaskID]_[설명].sql` | `S1D1_users_table.sql` |
| T (Testing) | `[대상].test.js` | `auth.test.js` |
| M (Documentation) | 자유 | `api-specification.md` |
| U (Design) | 자유 | `wireframe-v1.fig` |
| O (DevOps) | 자유 | `deploy-script.sh` |
| C (Content) | 자유 | `faq-data.json` |

---

## 체크리스트

- [ ] kebab-case 사용했는가?
- [ ] [기능]-[동작] 형식인가?
- [ ] 파일명만 보고 무슨 기능인지 알 수 있는가?
- [ ] Task ID를 파일 상단 주석에 넣었는가?
