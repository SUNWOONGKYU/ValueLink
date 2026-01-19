# DNS Setup Guide Template

## Overview

도메인 DNS 설정 가이드입니다.

---

## 1. DNS 레코드 종류

| 레코드 | 용도 | 예시 |
|--------|------|------|
| **A** | 도메인 → IP 주소 | `@ → 76.76.21.21` |
| **CNAME** | 도메인 → 다른 도메인 | `www → cname.vercel-dns.com` |
| **TXT** | 텍스트 정보 (인증용) | `_vercel → vc-domain-verify=...` |
| **MX** | 이메일 서버 | `@ → mail.example.com` |

---

## 2. Vercel 연결 시 DNS 설정

### 2.1 루트 도메인 (example.com)

#### A 레코드
```
호스트명: @ (또는 비워두기)
타입: A
값: 76.76.21.21
TTL: 자동 또는 300
```

### 2.2 www 서브도메인 (www.example.com)

#### CNAME 레코드
```
호스트명: www
타입: CNAME
값: cname.vercel-dns.com
TTL: 자동 또는 300
```

### 2.3 도메인 소유권 확인 (필요 시)

#### TXT 레코드
```
호스트명: _vercel
타입: TXT
값: vc-domain-verify=도메인,인증코드
TTL: 자동 또는 300
```

---

## 3. 이메일 서비스 DNS 설정

### 3.1 Resend 사용 시

#### MX 레코드
```
호스트명: @
타입: MX
값: feedback-smtp.resend.com
우선순위: 10
```

#### TXT 레코드 (SPF)
```
호스트명: @
타입: TXT
값: v=spf1 include:resend.com ~all
```

#### TXT 레코드 (DKIM)
```
호스트명: resend._domainkey
타입: TXT
값: (Resend Dashboard에서 제공)
```

---

## 4. DNS 전파 확인

### 4.1 확인 도구
- https://dnschecker.org/
- https://www.whatsmydns.net/

### 4.2 전파 시간
- **최소**: 5분
- **일반**: 1~4시간
- **최대**: 48시간

---

## 5. 도메인 등록 업체별 설정 위치

| 업체 | DNS 설정 위치 |
|------|--------------|
| Whois | 도메인 관리 → 부가서비스 → 네임서버 고급설정 |
| 가비아 | 도메인 관리 → DNS 관리 |
| 후이즈 | My도메인 → DNS 레코드 관리 |
| GoDaddy | 도메인 → DNS 관리 |
| Namecheap | Domain List → Advanced DNS |

---

## 6. 트러블슈팅

### 문제 1: 도메인 소유권 확인 실패
```
This domain is linked to another account.
```
**해결**: TXT 레코드 추가 후 DNS 전파 대기 (최대 48시간)

### 문제 2: SSL 인증서 발급 실패
**해결**: DNS 레코드가 올바르게 설정되었는지 확인

### 문제 3: www 접속 불가
**해결**: CNAME 레코드 확인

---

## 7. 체크리스트

- [ ] A 레코드 설정 (루트 도메인)
- [ ] CNAME 레코드 설정 (www)
- [ ] TXT 레코드 설정 (소유권 확인, 필요 시)
- [ ] DNS 전파 확인
- [ ] SSL 인증서 발급 확인

---

**Template Version**: 1.0
