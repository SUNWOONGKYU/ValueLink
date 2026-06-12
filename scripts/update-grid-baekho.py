# -*- coding: utf-8 -*-
# 백호 작전 잔여 마무리 — SAL Grid modification_history 갱신 (루트 + Process 원본 동시)
import json, io

ENTRIES = {
    "S2F4": "2026-06-12: 백호 작전 — 정적 HTML 22파일 supabase→supabaseClient 전역변수 리네임 (window.supabase UMD 섀도잉 제거). DW-1 레드팀 정적검증 CLEAN + 실브라우저 22/22 PASS (tests/echo-rename-error-check.js).",
    "S2F5": "2026-06-12: 백호 작전 보안 패치 — valuation 워크플로우 5페이지(accountant-review, data-collection, draft-generation, final-preparation, evaluation-progress) localStorage 역할위조 차단: 게이트 통과 시에도 Supabase 세션+DB role 2차 검증(runVerify + readyState 가드), 불일치 시 차단·위조값 제거. reviewer Verified. 위조차단 5/5 + 정상접근 3/3 PASS.",
    "S5T1": "2026-06-12: 백호 작전 검증 스크립트 3종 추가 — tests/echo-rename-error-check.js(22파일 식별자 에러 0건), tests/verify-role-spoof-patch.js(위조 차단 5/5 PASS), tests/verify-role-legit-path.js(e2e 실로그인 정상 접근 3/3 PASS).",
}

BASES = [
    "method/json/data/grid_records",
    "Process/S0_Project-SAL-Grid_생성/method/json/data/grid_records",
]

for base in BASES:
    for tid, entry in ENTRIES.items():
        path = f"{base}/{tid}.json"
        with io.open(path, encoding="utf-8") as f:
            d = json.load(f)
        mh = d.get("modification_history") or ""
        if entry in mh:
            print(f"skip(dup) {path}")
            continue
        d["modification_history"] = (mh + "\n" if mh else "") + entry
        d["updated_at"] = "2026-06-12"
        with io.open(path, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, indent=2)
        print(f"updated {path}")
print("done")
