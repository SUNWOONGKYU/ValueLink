# ValueLink 자동 커밋/푸시 스크립트
# 5분마다 실행되어 변경사항을 자동으로 GitHub에 커밋/푸시

$ErrorActionPreference = "Continue"
$ProjectPath = "C:\ValueLink"
$LogFile = Join-Path $ProjectPath "scripts\auto-commit.log"

# 로그 함수
function Write-Log {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] $Message"
    Add-Content -Path $LogFile -Value $logMessage
    Write-Host $logMessage
}

# 로그 시작
Write-Log "=== 자동 커밋 시작 ==="

try {
    # 프로젝트 디렉토리로 이동
    Set-Location $ProjectPath
    Write-Log "디렉토리: $ProjectPath"

    # Git 상태 확인
    $status = git status --porcelain 2>&1

    if ($LASTEXITCODE -ne 0) {
        Write-Log "ERROR: Git 상태 확인 실패 - $status"
        exit 1
    }

    # 변경사항이 있는지 확인
    if ([string]::IsNullOrWhiteSpace($status)) {
        Write-Log "변경사항 없음 - 커밋 건너뛰기"
        exit 0
    }

    # 변경된 파일 개수 확인
    $changedFiles = ($status -split "`n").Count
    Write-Log "변경된 파일: $changedFiles 개"

    # 모든 변경사항 스테이징
    git add -A 2>&1 | Out-Null

    if ($LASTEXITCODE -ne 0) {
        Write-Log "ERROR: git add 실패"
        exit 1
    }

    # 커밋 메시지 생성
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm"

    # 커밋 (한 줄 메시지)
    git commit -m "chore: auto-save $timestamp - $changedFiles files changed" 2>&1 | Out-Null

    if ($LASTEXITCODE -ne 0) {
        Write-Log "ERROR: git commit 실패"
        exit 1
    }

    Write-Log "커밋 완료: $changedFiles 개 파일"

    # GitHub에 푸시
    Write-Log "GitHub에 푸시 중..."
    $pushOutput = git push origin master 2>&1

    if ($LASTEXITCODE -ne 0) {
        Write-Log "ERROR: git push 실패 - $pushOutput"
        exit 1
    }

    Write-Log "푸시 완료 ✅"
    Write-Log "=== 자동 커밋 성공 ==="

} catch {
    Write-Log "ERROR: 예외 발생 - $($_.Exception.Message)"
    exit 1
}
