# PowerShell Script - Voice Input for Claude Code
# Windows + H alternative using System.Speech.Recognition
# Press Ctrl+C to stop

Add-Type -AssemblyName System.Speech
Add-Type -AssemblyName System.Windows.Forms

# Configuration
$language = "ko-KR"  # Korean language (change to "en-US" for English)

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "   Voice Input for Claude Code" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Language: $language" -ForegroundColor Yellow
Write-Host ""
Write-Host "Commands:" -ForegroundColor Yellow
Write-Host "  - Say anything to convert to text" -ForegroundColor White
Write-Host "  - Say 'enter' or '엔터' to press Enter" -ForegroundColor White
Write-Host "  - Say 'stop' or '종료' to quit" -ForegroundColor White
Write-Host ""
Write-Host "Tip: Focus on Claude Code window before speaking!" -ForegroundColor Magenta
Write-Host ""
Write-Host "Press Ctrl+C to stop." -ForegroundColor Gray
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Create speech recognition engine
try {
    $recognizer = New-Object System.Speech.Recognition.SpeechRecognitionEngine($language)
} catch {
    Write-Host "ERROR: Could not initialize speech recognition for $language" -ForegroundColor Red
    Write-Host "Trying default language..." -ForegroundColor Yellow
    try {
        $recognizer = New-Object System.Speech.Recognition.SpeechRecognitionEngine
    } catch {
        Write-Host "ERROR: Speech recognition not available on this system" -ForegroundColor Red
        Write-Host "Please install Windows Speech Recognition feature." -ForegroundColor Yellow
        exit 1
    }
}

# Use dictation grammar for free-form speech
$dictationGrammar = New-Object System.Speech.Recognition.DictationGrammar
$recognizer.LoadGrammar($dictationGrammar)

# Set input to default audio device
$recognizer.SetInputToDefaultAudioDevice()

# Text-to-speech for feedback
$speech = New-Object System.Speech.Synthesis.SpeechSynthesizer
$speech.Rate = 3
$speech.Volume = 50

Write-Host "Listening... (Speak now)" -ForegroundColor Green
Write-Host ""

# Audio feedback
[console]::beep(800, 200)

$running = $true

while ($running) {
    try {
        # Recognize speech (timeout 10 seconds)
        $result = $recognizer.Recognize([TimeSpan]::FromSeconds(10))

        if ($result -ne $null -and $result.Text -ne "") {
            $text = $result.Text
            $confidence = [math]::Round($result.Confidence * 100)

            Write-Host "Recognized ($confidence%): " -NoNewline -ForegroundColor Cyan
            Write-Host $text -ForegroundColor White

            # Check for stop commands
            if ($text -match "^(stop|quit|exit|terminate|종료|중지|그만)$") {
                Write-Host ""
                Write-Host "Stop command received. Exiting..." -ForegroundColor Yellow
                $running = $false
                break
            }

            # Check for enter command
            if ($text -match "^(enter|엔터|전송|보내기)$") {
                [System.Windows.Forms.SendKeys]::SendWait("{ENTER}")
                Write-Host "  -> [ENTER pressed]" -ForegroundColor Gray
                [console]::beep(600, 100)
            } else {
                # Type the recognized text
                # Escape special characters for SendKeys
                $escapedText = $text -replace '[\+\^\%\~\(\)\{\}\[\]]', '{$0}'

                [System.Windows.Forms.SendKeys]::SendWait($escapedText)
                [console]::beep(500, 100)
            }

            Write-Host ""
        }
    } catch {
        # Timeout or recognition error - just continue listening
        Write-Host "." -NoNewline -ForegroundColor DarkGray
    }
}

# Cleanup
$recognizer.Dispose()
$speech.Dispose()

Write-Host ""
Write-Host "Voice input stopped." -ForegroundColor Yellow
Write-Host ""
