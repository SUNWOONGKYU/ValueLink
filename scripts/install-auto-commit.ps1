# ValueLink 자동 커밋 작업 스케줄러 설치 스크립트

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  ValueLink 자동 커밋 설치" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

$ErrorActionPreference = "Stop"
$ProjectPath = "C:\ValueLink"
$ScriptPath = Join-Path $ProjectPath "scripts\auto-commit.ps1"
$TaskName = "ValueLink_AutoCommit"

# 관리자 권한 확인
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "⚠️  관리자 권한으로 실행해야 합니다!" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "다음 중 하나를 선택하세요:" -ForegroundColor Yellow
    Write-Host "1. PowerShell을 관리자 권한으로 다시 실행" -ForegroundColor Yellow
    Write-Host "2. 현재 사용자 권한으로 설치 (권장)" -ForegroundColor Green
    Write-Host ""
    $choice = Read-Host "선택 (1 또는 2)"

    if ($choice -eq "1") {
        Write-Host ""
        Write-Host "PowerShell을 우클릭하여 '관리자 권한으로 실행'하고" -ForegroundColor Yellow
        Write-Host "다음 명령어를 실행하세요:" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "cd C:\ValueLink\scripts" -ForegroundColor Cyan
        Write-Host ".\install-auto-commit.ps1" -ForegroundColor Cyan
        Write-Host ""
        pause
        exit
    }
}

Write-Host "✓ 스크립트 경로: $ScriptPath" -ForegroundColor Green

# 기존 작업 삭제
try {
    $existingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    if ($existingTask) {
        Write-Host ""
        Write-Host "기존 작업이 발견되었습니다. 삭제합니다..." -ForegroundColor Yellow
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
        Write-Host "✓ 기존 작업 삭제 완료" -ForegroundColor Green
    }
} catch {
    # 무시
}

# 작업 생성
Write-Host ""
Write-Host "작업 스케줄러에 등록 중..." -ForegroundColor Cyan

$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-WindowStyle Hidden -ExecutionPolicy Bypass -File `"$ScriptPath`""

# 5분마다 실행 트리거
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) -RepetitionInterval (New-TimeSpan -Minutes 5) -RepetitionDuration ([TimeSpan]::MaxValue)

# 설정
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 2)

# 현재 사용자로 실행
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -RunLevel Limited

# 작업 등록
try {
    Register-ScheduledTask `
        -TaskName $TaskName `
        -Action $action `
        -Trigger $trigger `
        -Settings $settings `
        -Principal $principal `
        -Description "ValueLink 프로젝트를 5분마다 자동으로 GitHub에 커밋/푸시합니다."

    Write-Host ""
    Write-Host "================================================" -ForegroundColor Green
    Write-Host "  설치 완료! ✅" -ForegroundColor Green
    Write-Host "================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "✓ 작업 이름: $TaskName" -ForegroundColor Green
    Write-Host "✓ 실행 주기: 5분마다" -ForegroundColor Green
    Write-Host "✓ 로그 파일: $ProjectPath\scripts\auto-commit.log" -ForegroundColor Green
    Write-Host ""
    Write-Host "작업이 백그라운드에서 자동 실행됩니다." -ForegroundColor Cyan
    Write-Host "변경사항이 있으면 5분마다 자동으로 커밋/푸시됩니다." -ForegroundColor Cyan
    Write-Host ""

    # 테스트 실행 제안
    Write-Host "지금 바로 테스트하시겠습니까? (Y/N): " -ForegroundColor Yellow -NoNewline
    $test = Read-Host

    if ($test -eq "Y" -or $test -eq "y") {
        Write-Host ""
        Write-Host "테스트 실행 중..." -ForegroundColor Cyan
        Start-ScheduledTask -TaskName $TaskName
        Start-Sleep -Seconds 2

        # 로그 확인
        $logPath = Join-Path $ProjectPath "scripts\auto-commit.log"
        if (Test-Path $logPath) {
            Write-Host ""
            Write-Host "=== 최근 로그 ===" -ForegroundColor Cyan
            Get-Content $logPath -Tail 10
        }
    }

    Write-Host ""
    Write-Host "작업 상태 확인: Get-ScheduledTask -TaskName '$TaskName'" -ForegroundColor Gray
    Write-Host "작업 삭제: Unregister-ScheduledTask -TaskName '$TaskName'" -ForegroundColor Gray
    Write-Host ""

} catch {
    Write-Host ""
    Write-Host "ERROR: 작업 등록 실패" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}

pause
