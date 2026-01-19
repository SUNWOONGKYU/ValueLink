#!/bin/sh
# ================================================
# Pre-commit Hook - 진행률 자동 업로드 예시
# ================================================
# 위치: .git/hooks/pre-commit
#
# 이 hook은 git commit 시 자동으로:
# 1. build-progress.js 실행 (진행률 계산)
# 2. upload-progress.js 실행 (DB 업로드)
# ================================================

PROJECT_ROOT="$(git rev-parse --show-toplevel)"

# === 진행률 빌드 (phase_progress.json 생성) ===
echo "📊 진행률 빌드 중..."
node "$PROJECT_ROOT/Development_Process_Monitor/build-progress.js"

if [ $? -ne 0 ]; then
    echo "⚠️ 진행률 빌드 실패 (계속 진행)"
fi

# 진행률 파일 스테이징에 추가
git add "$PROJECT_ROOT/Development_Process_Monitor/data/phase_progress.json" 2>/dev/null

# === 진행률 DB 업로드 ===
echo "📤 진행률 DB 업로드 중..."
node "$PROJECT_ROOT/scripts/upload-progress.js"

if [ $? -ne 0 ]; then
    echo "⚠️ 진행률 DB 업로드 실패 (계속 진행)"
fi

echo "✅ 진행률 처리 완료!"
exit 0
