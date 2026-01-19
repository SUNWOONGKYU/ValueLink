# Claude Code 음성 명령 스크립트
# 사용법: .\voice.ps1

Add-Type -AssemblyName System.Speech

$recognizer = New-Object System.Speech.Recognition.SpeechRecognitionEngine
$recognizer.SetInputToDefaultAudioDevice()

$grammar = New-Object System.Speech.Recognition.DictationGrammar
$recognizer.LoadGrammar($grammar)

Clear-Host
Write-Host ""
Write-Host " ======================================== " -ForegroundColor Cyan
Write-Host "    Claude Code 음성 명령                " -ForegroundColor Cyan
Write-Host " ======================================== " -ForegroundColor Cyan
Write-Host ""
Write-Host " 말하면 바로 Claude Code가 실행됩니다" -ForegroundColor White
Write-Host " 종료: Ctrl+C" -ForegroundColor DarkGray
Write-Host ""

try {
    while ($true) {
        Write-Host "----------------------------------------" -ForegroundColor DarkGray
        Write-Host "[대기중] 말하세요..." -ForegroundColor Yellow

        $result = $recognizer.Recognize()

        if ($result -and $result.Text -and $result.Text.Trim()) {
            $text = $result.Text.Trim()

            Write-Host ""
            Write-Host "[인식됨] " -NoNewline -ForegroundColor Green
            Write-Host $text -ForegroundColor White
            Write-Host ""
            Write-Host "[실행중] Claude Code..." -ForegroundColor Cyan
            Write-Host ""

            # Claude Code 실행
            $output = claude -p $text 2>&1

            Write-Host $output
            Write-Host ""
        }
    }
}
catch {
    Write-Host "오류: $_" -ForegroundColor Red
}
finally {
    $recognizer.Dispose()
    Write-Host ""
    Write-Host "종료됨" -ForegroundColor DarkGray
}
