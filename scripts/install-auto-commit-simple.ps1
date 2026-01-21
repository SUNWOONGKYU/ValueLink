# ValueLink 자동 커밋 작업 스케줄러 설치 스크립트 (간단 버전)

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  ValueLink 자동 커밋 설치" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

$ProjectPath = "C:\ValueLink"
$ScriptPath = Join-Path $ProjectPath "scripts\auto-commit.ps1"
$TaskName = "ValueLink_AutoCommit"
$UserName = $env:USERNAME

Write-Host "✓ 스크립트 경로: $ScriptPath" -ForegroundColor Green
Write-Host "✓ 작업 이름: $TaskName" -ForegroundColor Green
Write-Host ""

# 기존 작업 삭제
Write-Host "기존 작업 확인 중..." -ForegroundColor Cyan
schtasks /query /tn $TaskName 2>$null | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "기존 작업을 삭제합니다..." -ForegroundColor Yellow
    schtasks /delete /tn $TaskName /f | Out-Null
    Write-Host "✓ 기존 작업 삭제 완료" -ForegroundColor Green
}

# 작업 생성
Write-Host ""
Write-Host "작업 스케줄러에 등록 중..." -ForegroundColor Cyan

# schtasks 명령어 사용
$command = "powershell.exe"
$arguments = "-WindowStyle Hidden -ExecutionPolicy Bypass -File `"$ScriptPath`""

# 작업 생성 (5분마다 실행)
$result = schtasks /create `
    /tn $TaskName `
    /tr "$command $arguments" `
    /sc minute `
    /mo 5 `
    /ru $UserName `
    /f

if ($LASTEXITCODE -eq 0) {
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

    # 작업 상태 확인
    Write-Host "=== 작업 상태 ===" -ForegroundColor Cyan
    schtasks /query /tn $TaskName /fo LIST
    Write-Host ""

    # 테스트 실행 제안
    Write-Host "지금 바로 테스트하시겠습니까? (Y/N): " -ForegroundColor Yellow -NoNewline
    $test = Read-Host

    if ($test -eq "Y" -or $test -eq "y") {
        Write-Host ""
        Write-Host "테스트 실행 중..." -ForegroundColor Cyan
        schtasks /run /tn $TaskName
        Start-Sleep -Seconds 3

        # 로그 확인
        $logPath = Join-Path $ProjectPath "scripts\auto-commit.log"
        if (Test-Path $logPath) {
            Write-Host ""
            Write-Host "=== 최근 로그 ===" -ForegroundColor Cyan
            Get-Content $logPath -Tail 15
        } else {
            Write-Host ""
            Write-Host "로그 파일이 아직 생성되지 않았습니다." -ForegroundColor Yellow
            Write-Host "변경사항이 있을 때 자동으로 생성됩니다." -ForegroundColor Yellow
        }
    }

    Write-Host ""
    Write-Host "=== 관리 명령어 ===" -ForegroundColor Gray
    Write-Host "작업 상태 확인: schtasks /query /tn $TaskName" -ForegroundColor Gray
    Write-Host "작업 수동 실행: schtasks /run /tn $TaskName" -ForegroundColor Gray
    Write-Host "작업 삭제: schtasks /delete /tn $TaskName /f" -ForegroundColor Gray
    Write-Host ""

} else {
    Write-Host ""
    Write-Host "ERROR: 작업 등록 실패" -ForegroundColor Red
    Write-Host $result -ForegroundColor Red
    exit 1
}

pause
