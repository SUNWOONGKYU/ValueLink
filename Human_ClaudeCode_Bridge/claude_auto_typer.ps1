# PowerShell Script - Auto-type into Claude Code session
# Uses Windows Forms SendKeys to inject input

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Speech

$notificationFile = "C:\Your_Project_Path\Web_ClaudeCode_Bridge\.new_order_notification"
$checkInterval = 1000  # milliseconds

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "   Claude Code Auto-Typer RUNNING" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "This will automatically type into Claude Code when new orders arrive." -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop." -ForegroundColor Gray
Write-Host ""

# Text-to-speech for audio notification
$speech = New-Object System.Speech.Synthesis.SpeechSynthesizer
$speech.Rate = 2  # Speak faster

while ($true) {
    if (Test-Path $notificationFile) {
        try {
            # Read the notification
            Start-Sleep -Milliseconds 200  # Wait for file write to complete
            $content = Get-Content $notificationFile -Raw -Encoding UTF8 | ConvertFrom-Json

            $orderId = $content.order_id
            $orderContent = $content.content_korean
            $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

            Write-Host "[$timestamp] NEW ORDER DETECTED!" -ForegroundColor Green
            Write-Host "Order ID: $orderId" -ForegroundColor Yellow
            Write-Host "Content: $orderContent" -ForegroundColor White
            Write-Host ""

            # Find Claude Code window
            $claudeProcess = Get-Process | Where-Object {
                $_.MainWindowTitle -like "*Claude*" -or
                $_.ProcessName -eq "claude" -or
                $_.MainWindowTitle -like "*MINGW64*"
            } | Select-Object -First 1

            if ($claudeProcess) {
                Write-Host "Found Claude window: $($claudeProcess.MainWindowTitle)" -ForegroundColor Cyan

                # Activate the window
                $wshell = New-Object -ComObject wscript.shell
                $null = $wshell.AppActivate($claudeProcess.Id)
                Start-Sleep -Milliseconds 500

                # Prepare the message
                $message = @"
NEW ORDER ARRIVED!
Order ID: $orderId
Content: $orderContent

Please acknowledge and process this order.
"@

                # Type the message
                [System.Windows.Forms.SendKeys]::SendWait($message)
                [System.Windows.Forms.SendKeys]::SendWait("{ENTER}")

                # Audio notification
                $speech.SpeakAsync("New order received") | Out-Null

                # System beep
                [console]::beep(1000, 300)

                Write-Host "Message sent to Claude Code!" -ForegroundColor Green
                Write-Host ""

            } else {
                Write-Host "WARNING: Could not find Claude Code window" -ForegroundColor Red
                Write-Host "Make sure Claude Code is running in a visible window." -ForegroundColor Yellow
                Write-Host ""
            }

            # Delete the notification file
            Remove-Item $notificationFile -Force

        } catch {
            Write-Host "ERROR: $_" -ForegroundColor Red
            Write-Host ""
        }
    }

    Start-Sleep -Milliseconds $checkInterval
}
