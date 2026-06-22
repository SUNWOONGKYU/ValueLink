#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
회사명 검증 단위 테스트 v2
원칙: 거짓음성(실딜 누락) > 거짓양성(잡음 노출)
- MUST_REJECT: 명백한 일반어구/문장조각 — 반드시 거부
- MAY_PASS: 이름만으로는 애매 — 기사 게이트가 2차 방어하므로 통과해도 됨
- REGRESSION: 실제 회사명 58개 — 전부 PASS 필수
- INV_REJECT / INV_PASS: is_investment_news() 게이트 검증

실행: python test_company_validation.py
"""
import sys
import os

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except AttributeError:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(__file__))
import collect_naver_only as cn

# ──────────────────────────────────────────────────────────
# MUST_REJECT: 이름 자체가 명백히 일반어구/문장조각
# 기사 게이트와 무관하게 _valid_company()가 반드시 거부해야 함
# ──────────────────────────────────────────────────────────
MUST_REJECT = [
    # 2글자 명백 일반어
    ('사줘',            '2글자 동사어미'),
    ('추론',            '2글자 일반명사'),
    ('창업',            '2글자 일반명사'),
    ('창구',            '2글자 일반명사'),
    ('산단',            '2글자 일반명사'),
    ('외화',            '2글자 일반명사'),
    # 공백+1글자 한글 조각
    ('반도체 제',       '공백+1글자 조각'),
    ('혁신 창',         '공백+1글자 조각'),
    # 고유명사 토큰 전무한 일반 어구
    ('클라우드 기업',         'NOISE_COMPANY 완전일치'),
    ('우주 스타트업',         'NOISE_COMPANY 완전일치'),
    ('소부장·팹리스 기업',    'NOISE_COMPANY 완전일치'),
    ('오가노이드 스타트업',   'NOISE_COMPANY 완전일치'),
    ('유니콘 등극',           'BAD_TOKEN 잇따라/등극'),
    ('VC서 잇따라',           'BAD_TOKEN 잇따라'),
    ('지배적 디자인',         'NOISE_COMPANY'),
    ('사업 확장',             'NOISE_COMPANY'),
    ('총력 승리',             'NOISE_COMPANY'),
    ('한때 유니콘',           'NOISE_COMPANY'),
    ('미국은 빅테크',         '조사 은 + NOISE'),
]

# ──────────────────────────────────────────────────────────
# MAY_PASS: 이름 기반으로 구분 어려움 → 통과해도 무방
# 기사 게이트(is_investment_news) + 신뢰도 게이트(금액/투자자 필수)가 2차 방어
# 테스트에서는 pass/fail 모두 허용 — 결과만 표시
# ──────────────────────────────────────────────────────────
MAY_PASS = [
    ('등 딥테크',   '등으로 시작 — 기사 게이트로 처리'),
    ('유럽기업',    '일반접미사지만 짧음 — 기사 게이트로 처리'),
    ('호주 중심',   '일반 어구 — 기사 게이트로 처리'),
]

# ──────────────────────────────────────────────────────────
# REGRESSION: 실제 회사명 — 전부 PASS 필수
# ──────────────────────────────────────────────────────────
REGRESSION = [
    # 기존 검증 회사
    ('스패너',              '기존 DB'),
    ('유진로봇',            '기존 DB'),
    ('제로해시',            '기존 DB'),
    ('서킷허브',            '기존 DB'),
    ('코드잇',              '기존 DB'),
    ('데이터브릭스',        '기존 DB'),
    ('시그노스',            '기존 DB'),
    ('트웰브랩스',          '기존 DB'),
    ('바이트랩',            '기존 DB'),
    ('솔라 시큐리티',       '기존 DB(공백1)'),
    ('아즈텍랩스',          '기존 DB'),
    ('올릭스',              '기존 DB'),
    ('에피드게임즈',        '기존 DB'),
    ('크로스포인트',        '기존 DB'),
    ('솔트바이펩',          '기존 DB'),
    ('유앤소프트',          '기존 DB'),
    ('사운드리퍼블리카',    '기존 DB'),
    ('코스모비',            '기존 DB'),
    ('프라이빗테크놀로지',  '기존 DB'),
    ('빅모빌리티',          '기존 DB'),
    ('이노파마',            '기존 DB'),
    ('레티튜',              '기존 DB'),
    ('플라이투',            '기존 DB'),
    ('알체라',              '기존 DB'),
    ('와이어스톡',          '기존 DB'),
    ('치타부',              '기존 DB'),
    ('파운데이션',          '기존 DB'),
    ('디플리',              '기존 DB'),
    ('엑스포넌트',          '기존 DB'),
    ('리벨리온',            '기존 DB'),
    ('페달링',              '기존 DB'),
    ('아크',                '기존 DB(2글자 고유명)'),
    ('IST엔터',             '기존 DB(영문+한글)'),
    ('SK바이오팜',          '기존 DB'),
    # 신규 추가 — 오탈락 보고된 실회사 24개
    ('산군',                '실딜 — 브랜드명'),
    ('유비파이',            '실딜 — 이로 끝남'),
    ('에봄에이아이',        '실딜 — 이로 끝남'),
    ('베디베로',            '실딜 — 로로 끝남'),
    ('엑시나',              '실딜 — 나로 끝남'),
    ('아인스하나',          '실딜 — 나로 끝남'),
    ('1에스와이유',         '실딜 — 숫자 시작 브랜드'),
    ('에니아이',            '실딜 — 이로 끝남'),
    ('무인화연구소',        '실딜 — 연구소 포함 스타트업'),
    ('르페르소나',          '실딜 — 나로 끝남'),
    ('로카101',             '실딜 — 숫자 포함 브랜드'),
    ('엘케이벤처스',        '실딜 — 6글자 벤처스 브랜드'),
    ('소프트웨어융합연구소','실딜 — 연구소 포함 기관'),
    ('프랙타일',            '실딜'),
    ('업스테이지',          '실딜'),
    ('인터그래비티',        '실딜'),
    ('알세미',              '실딜'),
    ('스트레스솔루션',      '실딜'),
    ('직스에이아이',        '실딜 — 이로 끝남'),
    ('매니폴드 시큐리티',   '실딜 — 공백1'),
    ('셀트리온',            '실딜'),
    ('앤스로픽',            '실딜 — NOISE에서 제거됨'),
]

# ──────────────────────────────────────────────────────────
# is_investment_news() 게이트
# ──────────────────────────────────────────────────────────
INV_REJECT = [
    ("현근택, 선거운동 첫날 합동 출정식…총력 승리 100억원 투자",        '선거'),
    ("LIV 골프, 2027년 호주 중심 10개 국제 대회 검토 100억원",          'LIV골프'),
    ("미국은 빅테크, 중국은 국책펀드 AI 투자전 가속",                   '시장분석'),
    ("LH, 호주달러 채권 5375억원 조달 외화 조달처 확대",                '채권조달'),
    ("챗GPT가 벤처투자 판 바꿔 한때 유니콘 220곳 추락 100억원 투자",    '유니콘일반'),
]

INV_PASS = [
    ("스패너, 한투파·KB인베에 256억 투자 유치",                             '정상 투자뉴스'),
    ("시그노스, 301억원 시리즈A 투자 유치",                                 '정상 투자뉴스'),
    ("솔트바이펩, 블루포인트파트너스 등으로부터 프리 시리즈A 투자 유치",    '정상 투자뉴스'),
    ("앤스로픽, 엔비디아 주도 시리즈E 600억달러 투자 유치",                 '앤스로픽 정상'),
]

# ──────────────────────────────────────────────────────────
# AMOUNT: extract_amount() — 금액 추출/환산 검증 (억원 단위)
#   (text, expected) — expected None이면 추출 안 됨이 정답
#   환율 ≈ 1,350원/달러 기준: 만달러×0.135, 억달러×1350
# ──────────────────────────────────────────────────────────
AMOUNT_CASES = [
    # 억원 직접
    ("100억원 규모 시리즈A 투자 유치",   100,   '억원 직접'),
    ("약 50억 투자 유치",               50,    '억 직접'),
    ("1,000억원 투자",                  1000,  '천단위 콤마'),
    # 달러 환산 (이번 수정 핵심 회귀 방지)
    ("500만 달러 투자 유치",            68,    '만달러→억(500*0.135≈67.5)'),
    ("5000만 달러 시리즈B",             675,   '만달러→억(5000*0.135)'),
    ("1억 달러 투자 유치",              1350,  '억달러→억(1*1350)'),
    ("5억 달러 투자 라운드",            6750,  '억달러→억(5*1350)'),
    # 상한/오파싱 차단
    ("3조원 펀드 결성",                 None,  '조단위+펀드결성 노이즈'),
    ("기업가치 5000억 평가",            None,  '기업가치 노이즈 컨텍스트'),
    ("8억 달러 메가 투자",              None,  '억달러 환산>9999 상한 컷'),
    # 경계값
    ("1만 달러 시드 투자",              None,  '소액 만달러 round0→val<=0 None'),
    ("1조원 투자 유치",                 None,  '1조=10000억 상한(>9999) 컷'),
    ("100억원 시리즈B 투자",            100,   '억원+원? 정상(달러 부정선읽기 무영향)'),
]

# ──────────────────────────────────────────────────────────
def run():
    total_fail = 0

    # 1) MUST_REJECT
    print("=" * 65)
    print(f"[ MUST_REJECT {len(MUST_REJECT)}개 — _valid_company()가 반드시 거부 ]")
    print("=" * 65)
    mr_ok = 0
    mr_fail = []
    for cand, reason in MUST_REJECT:
        result = cn._valid_company(cand)
        ok = not result
        sym = "✓" if ok else "✗"
        tag = "거부됨" if ok else "통과됨!"
        print(f"  {sym} [{tag}] '{cand}'  ({reason})")
        if ok:
            mr_ok += 1
        else:
            mr_fail.append(cand)
    total_fail += len(mr_fail)

    # 2) MAY_PASS
    print()
    print("=" * 65)
    print(f"[ MAY_PASS {len(MAY_PASS)}개 — pass/fail 모두 허용, 참고용 ]")
    print("=" * 65)
    for cand, reason in MAY_PASS:
        result = cn._valid_company(cand)
        tag = "허용됨" if result else "거부됨"
        print(f"  - [{tag}] '{cand}'  ({reason})")

    # 3) REGRESSION
    print()
    print("=" * 65)
    print(f"[ REGRESSION {len(REGRESSION)}개 — 실회사, 전부 PASS 필수 ]")
    print("=" * 65)
    rg_ok = 0
    rg_fail = []
    for cand, reason in REGRESSION:
        result = cn._valid_company(cand)
        ok = result
        sym = "✓" if ok else "✗"
        tag = "허용됨" if ok else "거부됨!"
        print(f"  {sym} [{tag}] '{cand}'  ({reason})")
        if ok:
            rg_ok += 1
        else:
            rg_fail.append(cand)
    total_fail += len(rg_fail)

    # 4) INV_REJECT
    print()
    print("=" * 65)
    print(f"[ INV_REJECT {len(INV_REJECT)}개 — is_investment_news() 거부 필수 ]")
    print("=" * 65)
    ir_ok = 0
    ir_fail = []
    for text, reason in INV_REJECT:
        result = cn.is_investment_news(text)
        ok = not result
        sym = "✓" if ok else "✗"
        tag = "거부됨" if ok else "통과됨!"
        print(f"  {sym} [{tag}] ({reason})")
        if ok:
            ir_ok += 1
        else:
            ir_fail.append(reason)
    total_fail += len(ir_fail)

    # 5) INV_PASS
    print()
    print("=" * 65)
    print(f"[ INV_PASS {len(INV_PASS)}개 — is_investment_news() 허용 필수 ]")
    print("=" * 65)
    ip_ok = 0
    ip_fail = []
    for text, reason in INV_PASS:
        result = cn.is_investment_news(text)
        ok = result
        sym = "✓" if ok else "✗"
        tag = "허용됨" if ok else "거부됨!"
        print(f"  {sym} [{tag}] ({reason})")
        if ok:
            ip_ok += 1
        else:
            ip_fail.append(reason)
    total_fail += len(ip_fail)

    # 6) AMOUNT
    print()
    print("=" * 65)
    print(f"[ AMOUNT {len(AMOUNT_CASES)}개 — extract_amount() 환산/상한 검증 ]")
    print("=" * 65)
    am_ok = 0
    am_fail = []
    for text, expected, reason in AMOUNT_CASES:
        result = cn.extract_amount(text)
        ok = (result == expected)
        sym = "✓" if ok else "✗"
        print(f"  {sym} [{result}=={expected}] '{text}'  ({reason})")
        if ok:
            am_ok += 1
        else:
            am_fail.append((text, result, expected))
    total_fail += len(am_fail)

    # 요약
    print()
    print("=" * 65)
    print("[ 최종 결과 ]")
    print("=" * 65)
    print(f"  MUST_REJECT:  {mr_ok}/{len(MUST_REJECT)}  {'✓ ALL OK' if not mr_fail else '✗ FAIL: ' + str(mr_fail)}")
    print(f"  REGRESSION:   {rg_ok}/{len(REGRESSION)}  {'✓ ALL OK' if not rg_fail else '✗ FAIL: ' + str(rg_fail)}")
    print(f"  INV_REJECT:   {ir_ok}/{len(INV_REJECT)}  {'✓ ALL OK' if not ir_fail else '✗ FAIL: ' + str(ir_fail)}")
    print(f"  INV_PASS:     {ip_ok}/{len(INV_PASS)}  {'✓ ALL OK' if not ip_fail else '✗ FAIL: ' + str(ip_fail)}")
    print(f"  AMOUNT:       {am_ok}/{len(AMOUNT_CASES)}  {'✓ ALL OK' if not am_fail else '✗ FAIL: ' + str(am_fail)}")
    print()
    if total_fail == 0:
        print("  ALL REQUIRED TESTS PASSED")
    else:
        print(f"  {total_fail}개 필수 실패 — 수정 필요")
        sys.exit(1)

if __name__ == '__main__':
    run()
