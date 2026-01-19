# 03. Area/Stage 규칙

> 11개 Area와 5개 Stage 매핑

---

## 1. 11개 Area 목록

| # | 코드 | 영문명 | 한글명 | 폴더명 |
|---|------|--------|--------|--------|
| 1 | **M** | Documentation | 문서화 | `Documentation/` |
| 2 | **U** | Design | UI/UX 디자인 | `Design/` |
| 3 | **F** | Frontend | 프론트엔드 | `Frontend/` |
| 4 | **BI** | Backend Infrastructure | 백엔드 기반 | `Backend_Infra/` |
| 5 | **BA** | Backend APIs | 백엔드 API | `Backend_APIs/` |
| 6 | **D** | Database | 데이터베이스 | `Database/` |
| 7 | **S** | Security | 보안/인증/인가 | `Security/` |
| 8 | **T** | Testing | 테스트 | `Testing/` |
| 9 | **O** | DevOps | 운영/배포 | `DevOps/` |
| 10 | **E** | External | 외부 연동 | `External/` |
| 11 | **C** | Content System | 콘텐츠 시스템 | `Content_System/` |

---

## 2. 5개 Stage 목록

| # | 코드 | 영문명 | 한글명 | 주요 내용 | 폴더명 |
|---|------|--------|--------|----------|--------|
| 1 | **S1** | Development Setup | 개발 준비 | 환경설정, DB스키마, Auth설정 | `S1_개발_준비/` |
| 2 | **S2** | Auth & Registration | 개발 1차 | OAuth, 이메일, 회원가입 | `S2_개발-1차/` |
| 3 | **S3** | AI Integration | 개발 2차 | AI 연동, AI Q&A | `S3_개발-2차/` |
| 4 | **S4** | Payment & Admin | 개발 3차 | 결제, 관리자, 크레딧 | `S4_개발-3차/` |
| 5 | **S5** | Development Stabilization | 개발 마무리 | 배포, QA, 안정화 | `S5_개발_마무리/` |

---

## 3. Task ID 구조

**[Stage][Area][번호]**

```
S2BA1
│ │ └─ 순서: 1번째 Task
│ └─── Area: BA (Backend APIs)
└───── Stage: S2 (개발 1차)
```

**예시:**
| Task ID | Stage | Area | 순서 | 의미 |
|---------|-------|------|------|------|
| S1S1 | S1 | S | 1 | 개발준비 - 보안 - 1번 |
| S2F1 | S2 | F | 1 | 개발1차 - 프론트엔드 - 1번 |
| S2BA1 | S2 | BA | 1 | 개발1차 - 백엔드API - 1번 |
| S3E1 | S3 | E | 1 | 개발2차 - 외부연동 - 1번 |

---

## 4. 폴더 경로 예시

| Task ID | 폴더 경로 |
|---------|----------|
| S1S1 | `S1_개발_준비/Security/` |
| S1M1 | `S1_개발_준비/Documentation/` |
| S2F1 | `S2_개발-1차/Frontend/` |
| S2BA1 | `S2_개발-1차/Backend_APIs/` |
| S3E1 | `S3_개발-2차/External/` |

---

## 5. Area별 Production 저장 여부

| Area | Production 저장 | 이유 |
|------|:---------------:|------|
| F | ✅ | 배포 필요 |
| BA | ✅ | 배포 필요 |
| S | ✅ | 배포 필요 |
| BI | ✅ | 배포 필요 |
| E | ✅ | 배포 필요 |
| M | ❌ | 문서 |
| U | ❌ | 디자인 |
| D | ❌ | DB 직접 실행 |
| T | ❌ | 테스트 |
| O | ❌ | 설정 |
| C | ❌ | DB 저장 |

---

## 6. Area별 담당 Agent

| Area | Task Agent | Verification Agent |
|------|------------|-------------------|
| M | documentation-specialist | code-reviewer |
| U | frontend-developer | qa-specialist |
| F | frontend-developer | code-reviewer |
| BI | backend-developer | code-reviewer |
| BA | backend-developer | code-reviewer |
| D | database-specialist | database-specialist |
| S | security-specialist | security-auditor |
| T | test-engineer | qa-specialist |
| O | devops-troubleshooter | code-reviewer |
| E | backend-developer | code-reviewer |
| C | content-specialist | qa-specialist |

---

## 체크리스트

- [ ] Task ID에서 Stage, Area 정확히 파악했는가?
- [ ] 해당 Stage 폴더에 저장했는가?
- [ ] 해당 Area 폴더에 저장했는가?
- [ ] Production 저장 대상인지 확인했는가?
