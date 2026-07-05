# sync-valuelink-to-gdrive.ps1
# C:\ValueLink (마스터) → G:\내 드라이브\ValueLink (백업) 단방향 미러
# 예약 작업 "ValueLink_GDrive_Sync"가 로그온 시 자동 실행. 수동 실행도 가능.
# 주의: /MIR 이므로 G쪽에서만 수정한 파일은 다음 동기화 때 삭제/덮어쓰기됨. 작업은 반드시 C에서.

$src = 'C:\ValueLink'
$dst = 'G:\내 드라이브\ValueLink'
$logDir = 'C:\ValueLink\_WorkLog\sync-logs'
if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir | Out-Null }
$log = Join-Path $logDir ("sync_{0}.log" -f (Get-Date -Format 'yyyy_MM_dd__HH.mm'))

# G드라이브가 마운트 안 된 상태(드라이브 앱 미실행)면 /MIR이 대량 삭제로 오인될 수 있으므로 중단
if (-not (Test-Path $dst)) {
    "[$(Get-Date)] G드라이브 미마운트 — 동기화 건너뜀" | Out-File $log -Encoding utf8
    exit 1
}

robocopy $src $dst /MIR `
    /XD node_modules .next .swc playwright-report test-results 'sync-logs' `
    /R:2 /W:5 /MT:8 /NFL /NDL /NP /LOG:$log

$code = $LASTEXITCODE
"[$(Get-Date)] robocopy exit=$code (0~7=정상, 8+=오류)" | Out-File $log -Append -Encoding utf8

# 30일 지난 로그 정리
Get-ChildItem $logDir -Filter 'sync_*.log' | Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-30) } | Remove-Item -Force

exit ([int]($code -ge 8))
